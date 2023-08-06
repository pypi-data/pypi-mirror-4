"""


See LICENSE.txt for Licensing details
Copyright (c) <2013> <Samuel M. Smith>

"""


import sys
py = sys.version_info
py3k = py >= (3,0,0)

from collections import MutableMapping
from collections import OrderedDict

class MODict(MutableMapping):
    """ Multiple Ordered Dictionary. Inspired by other MultiDicts in the wild.
        Associated with each key is a list of values.
        Setting the value of an item appends the value to the list
        associated with the item key.
        Getting the value of an item returns the last
        item in the list associated with the item key.
        It behaves like an OrderedDict
        in that the order of item insertion is remembered.
        
        There are special methods available to access or replace or append to
        the full list of values for a given item key.
        Aliases method names to match other multidict like interfaces like
        webob.
    """

    def __init__(self, *pa, **kwa):
        """ MODict() -> new empty MODict instance.
                     
            MODict(pa1, pa2, ...) where pa = tuple of positional args,
            (pa1, pa2, ...) each paX may be  a sequence of duples (k,v) or a dict
        
            MODict(k1 = v1, k2 = v2, ...) where kwa = dictionary of keyword args,
            {k1: v1, k2 : v2, ...}
        """        
        self._dict = OrderedDict()
        self.update(*pa, **kwa)
    
    def update(self, *pa, **kwa):
        """ MODict.update(pa1, pa2, ...) where pa = tuple of positional args,
            (pa1, pa2, ...) each paX may be  a sequence of duples (k,v) or a dict
        
            MODict.update(k1 = v1, k2 = v2, ...) where kwa = dictionary of keyword args,
            {k1: v1, k2 : v2, ...}
        """        
        for a in pa:
            if isinstance(a, MODict): #positional arg is MODict
                for k, v in a.iterallitems():
                    self.append(k, v)
            elif hasattr(a,'get'): #positional arg is dictionary
               for k, v in a.iteritems():
                  self.append(k, v)
            else: #positional arg is sequence of duples (k,v)
               for k, v in a:
                  self.append(k, v)
     
        for k,v in kwa.iteritems():
            self.append(k, v)    
  
    
    def __len__(self): return len(self._dict)
    def __iter__(self): return iter(self._dict)
    def __contains__(self, key): return key in self._dict
    def __delitem__(self, key): del self._dict[key]
    def __getitem__(self, key): return self._dict[key][-1] #newest
    def __setitem__(self, key, value): self.append(key, value) #append
    def keys(self): return self._dict.keys()
    
    if py3k:
        def values(self): return (v[-1] for v in self._dict.values())
        def listvalues(self): return (v for v in self._dict.values())
        def allvalues(self):
            return (v for k, vl in self._dict.iteritems() for v in vl)          
        def items(self): return ((k, v[-1]) for k, v in self._dict.items())
        def listitems(self): return ((k, v) for k, v in self._dict.items())
        def allitems(self):
            return ((k, v) for k, vl in self._dict.items() for v in vl)
        iterkeys = keys
        itervalues = values
        iterlistvalues = listvalues
        iterallvalues = allvalues
        iteritems = items
        iterlistitems = listitems
        iterallitems = allitems
    
    else:
        def values(self): return [v[-1] for v in self._dict.values()]
        def listvalues(self): return [v for v in self._dict.values()]
        def allvalues(self): return [v for k, vl in self._dict.iteritems() for v in vl]
        def items(self): return [(k, v[-1]) for k, v in self._dict.items()]
        def listitems(self): return [(k, v) for k, v in self._dict.items()]
        def allitems(self):
            return [(k, v) for k, vl in self._dict.iteritems() for v in vl]
        
        def iterkeys(self): return self._dict.iterkeys()
        def itervalues(self): return (v[-1] for v in self._dict.itervalues())
        def iterlistvalues(self): return (v for v in self._dict.itervalues())
        def iterallvalues(self):
            return (v for k, vl in self._dict.iteritems() for v in vl)        
        def iteritems(self):
            return ((k, v[-1]) for k, v in self._dict.iteritems())
        def iterlistitems(self):
            return ((k, v) for k, v in self._dict.iteritems())        
        def iterallitems(self):
            return ((k, v) for k, vl in self._dict.iteritems() for v in vl)
    
    def has_key(self, key):
        return key in self
                
    def append(self, key, value):
        """ Add a new value to the list of values for this key. """
        self._dict.setdefault(key, []).append(value)
        
    def clear(self):
        self._dict.clear()
        
    def copy(self):
        return self.__class__(self)
    
    def get(self, key, default=None, index=-1, kind=None):
        """ Return the most recent value for a key, that is, the last element
            in the keyed item's value list. 
    
            default = value to be returned if the key is not
                present or the type conversion fails.
            index = index into the keyed item's value list.
            kind = callable is used to cast the value into a specific type.
                Exception are suppressed and result in the default value
                to be returned.
        """
        try:
            val = self._dict[key][index]
            return kind(val) if kind else val
        except Exception:
            pass
        return default
    
    def getlist(self, key):
        """ Return a (possibly empty) list of values for a key. """
        return self._dict.get(key) or []    
    
    def replace(self, key, value):
        """ Replace the list of values with a single value. """
        self._dict[key] = [value]
    
    def setdefault(self, key, default=None, kind=None):
        """ If key is in the dictionary, return the last (most recent) element
            from the keyed items's value list.
            
            If not, insert key with a value of default and return default.
            The default value of default is None.
            
            kind = callable is used to cast the returned value into a specific type.
            
            Exceptions are suppressed and result the default value being set
        """
        try:
            val = self._dict[key]
            return kind(val[-1]) if kind else val
        except Exception:
            self.append(key, default)
        return default
    
    
    def pop(self, key, *pa, **kwa):
        """ If key exists remove and return the indexed element of the key item
            list else return the optional following positional argument.
            If the optional positional arg is not provided and key does not exit
            then raise KeyError. If provided the index keyword arg determines
            which value in the key item list to return. Default is last element.
        """
        index = kwa.get('index', -1)
        try:
            val = self._dict.pop(key)
        except KeyError:
            if pa:
                return pa[0]
            else:
                raise 
        
        return val[index]
    
    def poplist(self, key, *pa):
        """ If key exists remove and return keyed item's value list,
            else return the optional following positional argument.
            If the optional positional arg is not provided and key does not exit
            then raise KeyError. 
            
        """
        try:
            val = self._dict.pop(key)
        except KeyError:
            if pa:
                return pa[0]
            else:
                raise 
        
        return val   
    
    def popitem(self, last=True, index=-1):
        """ Return and remove a key value pair. The index determines
            which value in the keyed item's value list to return.
            If last is True pop in LIFO order.
            If last is False pop in FIFO order.
        """
        key, val = self._dict.popitem(last=last)
        return (key, val[index])
    
    def poplistitem(self, last=True):
        """ Return and remove a key value list pair. 
            If last is True pop in LIFO order.
            If last is False pop in FIFO order.
        """
        return (self._dict.popitem(last=last))    
    
    def fromkeys(self, seq, default=None):
        """Return new MODict with keys from sequence seq with values set to default
        """
        return MODict((k, default) for k in seq)
    
    # aliases to mimic other multi-dict APIs 
    getone = get
    add = append
    popall = poplist