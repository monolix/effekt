# Copyright (c) 2019 Monolix
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from functools import wraps
from .errors import EventNotFound, TooLowPriority

class Effekt:
    def __init__(self, debug=False):
        # Initialize the listeners' dictionary
        self.listeners = {}

        """
        This dictionary has got a quite complex structure:
            {
                <event_name::str>: {
                    <priority::int>: [
                        <callback_func::function>,
                        ...
                    ],
                    ...
                },
                ...
            }
        Every event has a priority "list" (from 0 to infinity).
        Every value of the priority list has a list of callback functions.
        """

        # Set the debug mode
        self.debug = debug

        self.log("Entering debug mode", lvl="!")
    
    # Log a message if in debug mode
    def log(self, msg, emit="effekt", lvl="*"):
        if self.debug:
            print("[{0}][{1}] {2}".format(emit, lvl, msg))
        
        return True
    
    # Check if an event exists in the listeners' dictionary
    def _is_event_defined(self, event):
        self.log("Checking if the event is in the list")

        if event in self.listeners:
            return True
        
        return False

    # Check if the priority list is in the event
    def _is_priority_defined(self, event, pr):
        self.log("Checking if the priority list is registered in the event")

        if int(pr) in self.listeners[str(event)]:
            return True
        
        return False
    
    # Create the event's empty priority dictionary
    def _create_event(self, event):
        self.log("Creating the event")

        self.listeners[str(event)] = {}

    # Creating the priority's empty callback list
    def _create_priority(self, event, pr):
        self.log("Creating the priority list")

        self.listeners[str(event)][int(pr)] = []

    # Append a function to the callback list
    def _append_callback(self, event, pr, func):
        self.listeners[str(event)][int(pr)].append(func)

    # Execute all the callbacks in order
    def _exec_callbacks(self, event, kwargs):
        self.log("Executing all the callbacks with kwargs")

        # Cycle through the chosen event's priority list
        # the "dict.items()" method sorts the dictionary by key, so it can execute by priority
        for _, funcs in self.listeners[str(event)].items():
            # Cycle though the callback list
            for func in funcs:
                # Call all the callbacks with kwargs 
                func(**kwargs)
    
    # Register a callback to the event (default priority is 0)
    def on(self, event, pr=0):
        # Declare a decorator
        def decorator(func):
            self.log("Checking if priority is below 0 (negatives are not supported)")
            # Check if priority is less than zero
            if pr < 0:
                self.log("Is not", lvl="x")
                raise TooLowPriority("Cannot have priority less than 0.")
            
            # If not defined, create the event
            if not self._is_event_defined(event):
                self._create_event(event)

            # If not defined, create the priority
            if not self._is_priority_defined(event, pr):
                self._create_priority(event, pr)

            self.log("Appending the callback to the priority list")
            # Add the callback to the event
            self._append_callback(event, pr, func)

            return func
    
        # Return the decorator
        return decorator

    def emit(self, event, **kwargs):
        # Check if event is defined
        if not self._is_event_defined(event):
            self.log("Is not", lvl="x")
            raise EventNotFound("No events named '{}' found.".format(event))
        
        # Execute all the callbacks
        self._exec_callbacks(event, kwargs)

        # It's all fine - return True
        return True
