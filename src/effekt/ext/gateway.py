# Copyright (c) 2019 Monolix
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from .scratch import Scratch
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from sys import argv, exit
from datetime import datetime
from base64 import b64encode as encode, b64decode as decode
from json import dumps, loads
from re import compile

class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.address = (self.ip, self.port)
        self.server = None
        self.clients = []
        self.active = False

    def log(self, msg):
        # Print the log and the timestamp
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("[GATEWAY - {}] {}".format(now, msg))

    def broadcast(self, message, sender=None):
        self.log("Broadcasting...")
        for client in self.clients:
            if client != sender:
                client.send(message)

    def open_socket(self):
        try:
            self.server = socket(AF_INET, SOCK_STREAM)
            self.server.bind(self.address)
        except OSError as e:
            if self.server:
                self.server.close()
            self.log("Cannot bind to port, sorry...")
            exit(1)

    def run(self):
        self.open_socket()
        self.server.listen(5)

        self.active = True

        try:        
            while True:
                connection, (ip, port) = self.server.accept()

                self.log("New client connected!")

                c = Client(ip, port, connection, self)
                c.start()

                self.clients.append(c)
        except KeyboardInterrupt:
            self.close()

    def close(self):
        self.active = False
        self.server.close()

class Client(Thread):

    def __init__(self, ip, port, connection, server):
        super().__init__()

        self.connection = connection
        self.ip = ip
        self.port = port
        self.server = server

    def send(self, message):
        try: self.connection.send(message)
        except BrokenPipeError: pass

    def run(self):
        try:    
            while True:
                if not self.server.active:
                    self.connection.close()
                    return False
                
                # Receive data until it's finished
                data_received = self.connection.recv(4096)
                if not data_received: break

                self.server.log("Received data from {}".format(self.ip))
                
                # If it fails to unpack (decode) the message, ignore it
                if not self.unpack(data_received):
                    self.log("Invalid data, skipping message...")
                    continue

                self.server.log("-> {}".format(str(self.unpacked)))

                # Forward the message to everyone
                self.server.broadcast(data_received, sender=self)
        except KeyboardInterrupt:
            pass

    def unpack(self, msg):
        try:
            # Decode from base64
            decoded = decode(msg)
            # Decode from json
            decoded = loads(decoded.decode())
        except Exception as e:
            # The message is invalid
            self.server.log(e)
            return False
        
        # set the decoded message
        self.unpacked = decoded

        return True

class Gate(Scratch):

    def init(self):
        self._connected = False

    def _check_connection_uri(self, uri):
        valid = compile(r"^fkt:\/\/\w.+\S:[0-9]{4,5}$")
        if not valid.match(uri):
            return False
        return True
    
    def start(self):
        thread = Thread(target=self._receive_events)
        thread.start()
        self.log("Receiving thread started.")

    def connect(self, gate=None):
        if gate is None:
            gate = self.let.config.get("GATEWAY_CONNECTION_URI")
        
        if not self._check_connection_uri(gate):
            raise TypeError("Invalid connection URI. "
            "(Correct format: `fkt://<hostname>:<port>`).")
        
        gate = gate.split("fkt://")[1]
        self._host, self._port = gate.split(":")
        self._spawn_socket()
        self.start()

    def _spawn_socket(self):
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._connect_to_host()
    
    def _connect_to_host(self):
        try:
            self._socket.connect((self._host, int(self._port)))
            self._connected = True
        except ConnectionRefusedError:
            pass

    def _pack(self, data):
        to_send = dumps(data)
        to_send = encode(to_send.encode())

        self._to_send = to_send

    def _unpack(self):
        # Decode from base64
        decoded = decode(self._received)
        # Decode from json
        decoded = loads(decoded.decode())

        self._decoded = decoded

    def _send_request(self):
        try:
            if self._connected:
                self._socket.send(self._to_send)
                print("To send", self._to_send)
                return True
            else: return False
        except Exception as e:
            self.log("Cannot send data, raising exception...", "x")
            raise e
    
    def _parse_message(self):
        if not "event" in self._decoded: return False
        
        event = self._decoded["event"]

        if not "payload" in self._decoded:
            payload = {}
        else:
            payload = self._decoded["payload"]
        
        try:
            self.let.emit(event, **payload)
            return True
        except TypeError:
            return False

    def _receive_events(self):
        while self._connected:
            self._received = self._socket.recv(8192)
            if not self._received: break

            self._unpack()

            self._parse_message()

    def emit(self, event, **kwargs):
        self._pack({
            "event": event,
            "payload": kwargs
        })

        self._send_request()

    def close(self):
        self._connected = False
        self._socket.close()

if __name__ == "__main__":
    
    port = int(argv[1])

    server = Server("localhost", port)
    
    server.log("Starting Gateway...")
    server.run()
