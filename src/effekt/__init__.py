# Copyright (c) 2019 Emanuele Lillo
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from functools import wraps

class Effekt:
    def __init__(self, debug=False):
        self.listeners = {}
        self.debug = debug
        self.log("Entering debug mode", lvl="!")
    
    def log(self, msg, emit="effekt", lvl="*"):
        if self.debug:
            print("[{0}][{1}] {2}".format(emit, lvl, msg))
        return True
    
    def on(self, event, pr=0):
        def decorator(func):
            self.log("Checking if priority is below 0 (negatives are not supported)")
            if pr < 0:
                self.log("Is not", lvl="x")
                return func

            self.log("Checking if the event is in the list")
            if not event in self.listeners:
                self.log("Creating the event")
                self.listeners[str(event)] = {}

            self.log("Checking if the priority list is registered in the event")
            if not int(pr) in self.listeners[str(event)]:
                self.log("Creating the priority list")
                self.listeners[str(event)][int(pr)] = []

            self.log("Appending the function to the priority list")
            self.listeners[str(event)][int(pr)].append(func)

            return func
        return decorator

    def emit(self, event, **kwargs):
        self.log("Checking if event is in the listeners list")
        if str(event) not in self.listeners:
            self.log("Is not", lvl="x")
            return -1
        
        self.log("Executing all the events with kwargs")
        for key, value in self.listeners.items():
            if key == event:
                for _, funcs in value.items():
                    for func in funcs:
                        func(**kwargs)

        return 0
