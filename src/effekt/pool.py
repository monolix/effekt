# Copyright (c) 2019 Monolix
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from .router import Router
import sys, datetime as dt, threading as th
from re import compile
from socket import socket, AF_INET, SOCK_STREAM
from base64 import b64encode as encode, b64decode as decode
from json import dumps, loads
from threading import Thread

class Pool:
    def __init__(self, uri="fkt://localhost:6789"):
        self.connected = False
        self.routers = []
        self._format_uri(uri)
        self.connect()
    
    def _format_uri(self, uri):
        valid = compile(r"^fkt:\/\/\w.+\S:[0-9]{4,5}$")

        if not valid.match(uri):
            raise TypeError("Invalid connection URI. "
            "(Correct format: `fkt://<hostname>:<port>`).")
        
        self.uri = uri
        host = self.uri.split("fkt://")[1]
        self.host, self.port = host.split(":")
    
    def _spawn_socket(self):
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._connect_to_host()
    
    def _connect_to_host(self):
        try:
            self._socket.connect((self.host, int(self.port)))
            self.connected = True
        except ConnectionRefusedError:
            pass

    def _pack(self, data):
        dumped = dumps(data)
        encoded = encode(dumped.encode())

        return encoded
    
    def _unpack(self, encoded):
        decoded = decode(encoded)
        data = loads(decoded.decode())

        return data
    
    def _incoming_data(self):
        try:
            while self.connected:
                try:
                    received = self._socket.recv(8192)
                except BrokenPipeError:
                    self.connected = False
                    self._spawn_socket()
                    break
                if not received: break
            
                event = self._unpack(data)

                self._proxy_in(event)
        except KeyboardInterrupt:
            self._socket.close()

    def _proxy_in(self, event):
        name = event["event"]
        payload = event["payload"]

        for router, passive in self.routers:
            router.fire(name, **payload)

    def _send(self, data):
        if self.connected:
            try:
                self._socket.send(data)
            except BrokenPipeError:
                self.connected = False
                self._spawn_socket()

    def attach(self, router, passive=False):
        if not isinstance(router, Router):
            raise TypeError("Can only attach Routers, not cats! ~.~")
        
        self.routers.append((router, passive))

        if not passive:
            router._extensions.append(self)
        
    def on_event(self, event, **kwargs):
        encoded = self._pack({
            "event": event,
            "payload": kwargs
        })

        self._send(encoded)

    def connect(self):
        self._spawn_socket()
        
        thread = Thread(target=self._incoming_data)
        thread.start()

class PoolServer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.active = False
        self._server = None
        self.clients = []
        self._spawn_socket()

    def log(self, msg):
        now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sys.stdout.write("[SERVER - {}] {}\n".format(now, msg))
        sys.stdout.flush()

    def _spawn_socket(self):
        try:
            self._server = socket(AF_INET, SOCK_STREAM)
            self._server.bind((self.ip, self.port))
        except OSError:
            self.log("Cannot bind to port... sorry! :(")
            self.close()
    
    def _pack(self, data):
        dumped = dumps(data)
        encoded = encode(dumped.encode())

        return encoded
    
    def _unpack(self, encoded):
        decoded = decode(encoded)
        data = loads(decoded.decode())

        return data

    def _client(self, connection, address):
        try:
            while self.active:
                received = connection.recv(4096)
                if not received: break
                
                self.log("New data from {}! UwU".format(address[0]))

                try:
                    decoded = self._unpack(received)
                except:
                    self.log("Oopsie Whoopsie! The message is invalid.")
                    self.log("Skipping...")
                    continue
                
                self.log("-> {}".format(str(decoded)))

                self.broadcast(received, sender=(connection, address))
        except KeyboardInterrupt:
            self._server.close()

    def broadcast(self, message, sender=None):
        self.log("Broadcasting...")
        for client in self.clients:
            if client != sender:
                try:
                    self._server.send(message)
                except BrokenPipeError:
                    self.clients.remove(sender)
                    self.log("Dropped a broken client (ﾉ´・ω・)ﾉ ﾐ ┸━┸")
    
    def close(self):
        self.log("Shutting down...")
        if self._server:
            self._server.close()
        
        self.active = False
        sys.exit(1)

    def run(self):
        self._spawn_socket()
        self._server.listen(5)

        self.active = True

        try:
            while True:
                connection, address = self._server.accept()

                self.log("New client sir! - {}".format(address[0]))

                self.clients.append((connection, address))

                thread = th.Thread(
                    target=self._client, 
                    args=(connection, address)
                )

                thread.daemon = True
                thread.start()
        except KeyboardInterrupt:
            self._server.close()


if __name__ == "__main__":
    server = PoolServer("localhost", 6677)

    server.log("Started command line mode.")
    server.run()