# Copyright (c) 2019 Monolix
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from .scratch import Scratch
import time
from threading import Thread

class Clock(Scratch):

    # Basic Extension info
    AUTHOR = "The Monolix Team"
    ABOUT = "Simple time-based event emitting extension by {AUTHOR}"

    def init(self):
        # Set the clock's default state
        self.active = False

    def activate(self):
        # Set the clock's state to activated
        self.log("Activating the clock")
        self.active = True

    def stop(self):
        # Set the clock's state to deactivated 
        self.log("Deactivating the clock")
        self.active = False

    def _blocking_tick(self, event, relax, **kwargs):
        self.log("Entering the blocking tick")
        try:
            # Always emit events through the instance every relax seconds
            while self.active:
                self.let.emit(event, **kwargs)
                time.sleep(relax)
        # Catch CTRL-C presses
        except KeyboardInterrupt:
            self.log("Interrupting the tick by CRTL-C", "x")
            return 0

    def tick(self, event, relax=1, thread=False, **kwargs):
        # Activate the clock
        self.activate()
        self.log("Checking if the tick will be threaded")
        if not thread:
            # Start the ticking of the clock on the main thread
            self.log("Is not", lvl="f")
            self._blocking_tick(event, relax, **kwargs)
        else:
            # Spawn a new thread and start the ticking on it
            self.log("Starting a new thread", lvl="t")
            t = Thread(target=self._blocking_tick, args=(event, relax), kwargs=kwargs)
            t.start()
