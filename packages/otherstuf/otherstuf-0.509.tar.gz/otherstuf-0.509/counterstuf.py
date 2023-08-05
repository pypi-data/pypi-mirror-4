"""
Sidecar to `stuf` that adds `Counter`-like 
container `counterstuf`
"""

from collections import Counter

class counterstuf(Counter):
    """stuf-like surfacing of Counter"""
    
    def __getattr__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            return self[key]

    def __setattr__(self, key, value):
        if key in self.__dict__:
            self.__dict__[key] = value
        else:
            self[key] = value
        
    def update_self(self, *args, **kwargs):
        self.update(*args, **kwargs)
        return self
    
    def copy(self):
        return counterstuf(Counter.copy(self))
