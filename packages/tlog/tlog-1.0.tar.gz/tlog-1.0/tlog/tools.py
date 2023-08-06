import socket
from struct import pack

class rec(dict):    
    def __init__(self, def_val=None):
        dict.__init__(self)
        super(rec, self).__setattr__('def_val', def_val)

    def __getattr__(self, k):
        try:
            return self[k]
        except:
            if self.def_val is not None:                
                self[k] = self.def_val
                return self.def_val
            pass
        
    def __setattr__(self, k, v):
        self[k] = v

class rec_dict(dict):
                    
    def __init__(self):
        dict.__init__(self)

    def __getitem__(self, k):
        self[k] = self.get(k, rec())
        return super(rec_dict, self).get(k, None)

class sum_dict(dict):
    def __init__(self, def_val=0):
        dict.__init__(self)
        self.def_val = 0

    def add(self, key, val):
        try:
            self[key] += val
        except KeyError:
            self[key] = self.def_val + val

    def _or(self, key, val):
        self[key] = self.get(key, 0) | val

    def add_to_set(self, key, val):
        self[key] = self.get(key, set())
        self[key].add (val)

def ipstr(i):
    return socket.inet_ntoa ( pack ( 'I', i ) )
