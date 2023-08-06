"""


See LICENSE.txt for Licensing details
Copyright (c) <2013> <Samuel M. Smith>

"""
import sys
py = sys.version_info
py3k = py >= (3,0,0)

from collections import MutableMapping
if sys.version_info[1] < 7: #python 2.6 or earlier
    from  ordereddict import OrderedDict
else:
    from collections import OrderedDict

class LODict(OrderedDict):
    """ Lowercase OrderedDict
        ensures that all keys are lower case.
    """
    def __init__(self, *pa, **kwa):
        """ LODict() -> new empty LODict instance.
                     
            LODict(pa1, pa2, ...) where pa = tuple of positional args,
            (pa1, pa2, ...) each paX may be  a sequence of duples (k,v) or a dict
        
            LODict(k1 = v1, k2 = v2, ...) where kwa = dictionary of keyword args,
            {k1: v1, k2 : v2, ...}
        """
        super(LODict, self).__init__() #must do this first
        self.update(*pa, **kwa)
    
    def update(self, *pa, **kwa):
        """ LODict.update(pa1, pa2, ...) where pa = tuple of positional args,
            (pa1, pa2, ...) each paX may be  a sequence of duples (k,v) or a dict
        
            LODict.update(k1 = v1, k2 = v2, ...) where kwa = dictionary of keyword args,
            {k1: v1, k2 : v2, ...}
        """
        d = OrderedDict()
        for a in pa:
            if hasattr(a,'get'): #positional arg is dictionary
               for k, v in a.iteritems():
                  d[k.lower()] = v
            else: #positional arg is sequence of duples (k,v)
               for k, v in a:
                  d[k.lower()] = v
     
        for k, v in kwa.iteritems():
            d[k.lower()] = v
        
        super(LODict, self).update(d)
    
    
    def __setitem__(self, key, val):
        """ Make key lowercalse then setitem """
        super(LODict, self).__setitem__(key.lower(), val)
    
    def __delitem__(self, key):
        """ Make key lowercase then delitem """
        super(LODict, self).__delitem__(key.lower())
    
    def __contains__(self, key):
        """ Make key lowercase then test for inclusion"""
        return super(LODict, self).__contains__(key.lower())
        
    def __getitem__(self, key):
        return super(LODict, self).__getitem__(key.lower())
