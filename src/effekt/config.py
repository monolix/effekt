# Copyright (c) 2019 Monolix
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from json import load, JSONDecodeError

class ConfigObject:
    def __init__(self, initialized={}):
        self._config = initialized
    
    def set(self, key, value):
        self._config[key] = value
        return True

    def get(self, key):
        if key not in self._config:
            return None

        return self._config[key]
    
    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        return self.set(key, value)

    def load(self, filename="config.json"):
        try:
            with open(filename, "r") as f:
                try:
                    new_config = load(f)
                except JSONDecodeError:
                    return None
        except FileNotFoundError:
            return None

        self._config.update(new_config)