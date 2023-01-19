"""
***Eric's Special Sauce***

This module enables you to store dictionary-like data
in a method that can be quickly accessed and queried.
Made to replace pandas for small datasets, or API testing.
"""
from typing import Iterable

def lambda_debug(lambda_,param,debug=False):
    """Prints a debug message if debug is True."""
    if debug:
        print(lambda_,param)
    return lambda_

class Collection:
    """A table like object"""
    def __init__(self, data:list, name:str = None):
        if data is None:
            data = []
        self.data = [(Object(d) if not isinstance(d,Object) else d) for d in data]
        self.name = name if name is not None else ""
    def __getitem__(self, val):
        if isinstance(val, Iterable):
            return Object(
                dict(
                    list(
                        map(
                            lambda v: (
                                v,
                                list(
                                    map(
                                        lambda d: d.get(v),self.data
                                    )
                                )
                            ), val
                        )
                    )
                )
            )
        return Collection(self.data[val])
    def __repr__(self):
        return (self.name + (" = ")*(len(self.name)>0))+self.data.__str__()
    def __name__(self, name):
        self.name = name
        return self
    def where(self, *conditionals, debug=False):
        """Used to define conditionals to make a selection from the collection"""
        return Collection(list(filter(lambda o:(
            all(lambda_debug([c(o) for c in list(conditionals)],o,debug=debug))
        ),self.data)))
    def drop(self, *keys):
        """Remove keys from all objects in the collection"""
        def prune(data_object,keys_):
            for k in keys_:
                if k in data_object.keys():
                    data_object.pop(k)
                return data_object
        return Collection(list(map(lambda d: prune(d,keys), self.data)))

class Object:
    """A dictionary-like object that can call keys as attributes
        Making a call to the attribute "obj.attr" instead of "obj['attr']" """
    def __init__(self,mapping:dict = None):
        self.__dict__.update(mapping)
    def __setitem__(self, key, value):
        setattr(self, key, value)
    def __getitem__(self, key):
        if isinstance(key, dict):
            raise TypeError("attributes cannot be a dictionary")
        if isinstance(key,Iterable):
            return Object(dict(list(map(lambda k: (k,getattr(self,k)),key))))
        return getattr(key)

    def __repr__(self):
        return str(self.__dict__)
    def __str__(self):
        return str(self.__dict__)

    def pop(self,key):
        """Pops the value of a key from the object"""
        return self.__dict__.pop(key)
    def get(self,key,default=None):
        """Returns the value of a key if it exists"""
        return self.__dict__.get(key,default)

    def keys(self):
        """Returns a list of keys"""
        return self.__dict__.keys()
    def attributes(self):
        """Returns a list of attributes"""
        return self.__dict__.keys()
    def values(self):
        """ Returns the values of the object """
        return self.__dict__.values()
    def items(self):
        """Returns key,value pairs of the object"""
        return self.__dict__.items()

class ConditionalsPRIVATE:
    """A supporting object to enhance the experience when using a collection's 'where' function."""
    def __init__(self,k):
        self.key = k
    def __getitem__(self,key):
        self.key = key
        return self
    def __getattr__(self,key):
        self.key = key
        return self
    def debug(self,parm_x,parm_y,lambda_f, debug=False):
        """Debug lambdas"""
        if debug:
            print(parm_x,parm_y)
        return lambda_f(parm_x,parm_y)
    def __gt__(self,parm, debug=False):
        return lambda o: self.debug(o.get(self.key), parm, lambda x,y: x>y, debug=debug)

    def __lt__(self,parm, debug=False):
        return lambda o: self.debug(o.get(self.key), parm, lambda x,y: x<y, debug=debug)
    def __eq__(self,parm, debug=False):
        return lambda o: self.debug(o.get(self.key), parm, lambda x,y: x==y, debug=debug)
    def matches(self,parm, debug=False):
        """Similar to 'in' operator"""
        return lambda o: self.debug(o.get(self.key), parm, lambda x,y: x in y, debug=debug)

def field(name):
    """Simplifies Condition calls"""
    return ConditionalsPRIVATE(name)

def condition(key, func, value):
    """Implements conditionals in an english-like manner"""
    func_map = {
        ">": (lambda k,v: ConditionalsPRIVATE(k)>v),
        "<": (lambda k,v: ConditionalsPRIVATE(k)<v),
        "==": (lambda k,v: ConditionalsPRIVATE(k)==v),
        "matches": (lambda k,v: ConditionalsPRIVATE(k).matches(v))
    }
    return func_map[func](key,value)
