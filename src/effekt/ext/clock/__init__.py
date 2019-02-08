# Copyright (c) 2019 Monolix
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import time
from threading import Thread

class Clock:
    def __init__(self, let=None):
        if let is None:
            self.initialized = False
            return None
        
        self.init_ext(let)

    def init_ext(self, let):
        self.let = let
        self.initialized = True
        self.active = False
        self.let.log("'Clock' extension loaded", "ext.clock")

    def activate(self):
        self.let.log("Activating the clock", "ext.clock")
        self.active = True

    def stop(self):
        self.let.log("Deactivating the clock", "ext.clock")
        self.active = False

    def _blocking_tick(self, event, relax, **kwargs):
        self.let.log("Entering the blocking tick", "ext.clock")
        try:
            while self.active:
                self.let.emit(event, **kwargs)
                time.sleep(relax)
        except KeyboardInterrupt:
            self.let.log("Interrupting the tick by CRTL-C", "ext.clock", "x")
            return 0

    def tick(self, event, relax=1, thread=False, **kwargs):
        self.activate()
        self.let.log("Checking if the tick will be threaded", "ext.clock")
        if not thread:
            self.let.log("Is not", "ext.clock", lvl="f")
            self._blocking_tick(event, relax, **kwargs)
        else:
            self.let.log("Starting a new thread", "ext.clock", lvl="t")
            t = Thread(target=self._blocking_tick, args=(event, relax), kwargs=kwargs)
            t.start()
