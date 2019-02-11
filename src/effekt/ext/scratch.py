# Copyright (c) 2019 Monolix
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

class Scratch:
    def __init__(self, let=None):
        # If name not declared, set the name to the class name
        if not hasattr(self, "NAME"):
            self.name = self.__class__.__name__
        
        # If about information not found, set the docstring as about
        if not hasattr(self, "ABOUT"):
            if __doc__ is not None:
                self.ABOUT = self.__doc__

        # Variable used to check if the extension is initialized
        self.initialized = False
        
        # Placeholder for the "let" variable (Effekt instance)
        self.let = None
        
        # Check if the user passed the Effekt instance
        if let is None:
            return None
        
        # Initialize the extension with the instance
        self.init_ext(let)
    
    def __repr__(self):
        # Fancy formatting for representation
        return "<EffektExtension('{}')>".format(self.name)

    @property
    def about(self):
        # Return informations about the extension
        return getattr(self, "ABOUT", "No info provided") \
            .format(AUTHOR=getattr(self, "AUTHOR", "Unknown"))

    def log(self, msg, lvl="*"):
        # Do nothing til the extension is initialized
        if not self.initialized:
            return None
        
        # Log (if in debug mode) with the Effekt's logger
        return self.let.log(msg, "ext:{}".format(self.name), lvl)
    
    def init_ext(self, let):
        # Assign the instance
        self.let = let
        
        # Set the state to initialized
        self.initialized = True
        
        # Log the initialization
        self.log("Extension loaded")

        # Try to execute the ".init" method (defined by the user)
        try: self.init()
        except: pass
