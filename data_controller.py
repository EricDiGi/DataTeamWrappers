"""
***Eric's Special Sauce***

This module enables you to store dictionary-like data
in a method that can be quickly accessed and queried.
Made to replace pandas for small datasets, or API testing.
"""
from typing import Iterable
import re
import json

def lambda_debug(lambda_,param,debug=False):
    """Prints a debug message if debug is True."""
    if debug:
        print(lambda_,param)
    return lambda_

def access_if_key_exists(elem, key):
    if key in elem.keys:
        return elem.get(key)
    else:
        return None

class Collection:
    """A table like object"""
    def __init__(self, data:list, name:str = None):
        if data is None:
            data = []
        self.data = [(Object(d) if not isinstance(d,Object) else d) for d in data]
        self.name = name if name is not None else ""
    def __getitem__(self, val):
        if isinstance(val, Iterable):
            return Collection(list(
                map(lambda d: d[val],self.data)
            ))
        if isinstance(val, int):
            return self.data[val]
        if isinstance(val,slice):
            return Collection(self.data[val])
        raise TypeError("Cannot index with type {}".format(type(val)))
    def __repr__(self):
        return (self.name + (" = ")*(len(self.name)>0))+self.data.__str__()
    def __name__(self, name):
        self.name = name
        return self
    def __len__(self):
        return len(self.data)
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
    def __add__(self, other):
        if isinstance(other, Collection):
            self.data += other.data
        if isinstance(other, list):
            self.data += other
        if isinstance(other, Object):
            self.data.append(other)
        return self
    def unique(self, *attr):
        """Returns a list of unique values for a given attribute list
            Takes any amount of fields as parameters f(a,b,c,...)
        """
        if sorted(list(set(attr).intersection(set(self.columns)))) == sorted(attr):
            return Collection(
                list(
                    map(dict,
                    set(tuple(sorted(sub[attr].items())) for sub in self.data)
                    )
                )
            )
        outliers = list(set(attr)-set(attr).intersection(set(self.columns)))
        raise AttributeError(f"Invalid Attribute selection {outliers}")
    @property
    def columns(self):
        """Return a list of all unique keys in the Collection"""
        return list(set().union(*(list(map(lambda d: d.keys,self.data)))))
    # Tranpose the collection into dict of lists
    @property
    def T(self):
        """Transpose the Collection into a dict of lists"""
        return Object(dict(list(map(lambda col: (col,list(map(lambda e: access_if_key_exists(e,col),self.data))),self.columns))))
    def _repr_html_(self) -> str | None:
        presentation = {
            "header": self.columns,
            "content": list(map(lambda x: list(map(lambda k: access_if_key_exists(x,k),self.columns)),self.data))
        }
        return HtmlTable(presentation).html

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
            return Object(dict(list(map(lambda k: (k,None if (k not in self.keys) else getattr(self,k)),key))))
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
    @property
    def keys(self):
        """Returns a list of keys"""
        return list(self.__dict__.keys())
    @property
    def attributes(self):
        """Returns a list of attributes"""
        return list(self.__dict__.keys())
    def values(self):
        """ Returns the values of the object """
        return self.__dict__.values()
    def items(self):
        """Returns key,value pairs of the object"""
        return self.__dict__.items()
    def _repr_html_(self):
        pretty_json = json.dumps(self.__dict__,indent=2)
        pretty_json = pretty_json.replace('\n',"<br/>").replace('\t','&nbsp;&nbsp;')
        return HtmlCode(pretty_json).html


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
    def regex_match(self,parm,debug=False):
        if not isinstance(parm, tuple):
            raise TypeError("ragex_match was expecting a tuple not {}".format(type(parm)))
        return lambda o: self.debug(o.get(self.key), parm, lambda x,y: re.search(y[0],x,y[1]), debug=debug)

def field(name):
    """Simplifies Condition calls"""
    return ConditionalsPRIVATE(name)

def condition(key, func, value):
    """Implements conditionals in an english-like manner"""
    func_map = {
        ">": (lambda k,v: ConditionalsPRIVATE(k)>v),
        "<": (lambda k,v: ConditionalsPRIVATE(k)<v),
        "==": (lambda k,v: ConditionalsPRIVATE(k)==v),
        "matches": (lambda k,v: ConditionalsPRIVATE(k).matches(v)),
        "regex_match": (lambda k,v: ConditionalsPRIVATE(k).regex_match(v)),
    }
    return func_map[func](key,value)

class HtmlTable:
    def __init__(self, data):
        self.html = f"<html>{self.table(**data)}</html>"
    def td(self, item, c = None):
        if isinstance(c,list):
            cls = ' '.join(c)
        else:
            cls = c
        return f"<td {f'class={cls}' if c is not None else ''}>{str(item)}</td>"
    def tr(self, row, row_num):
        shades = ['light','dark']
        return f"<tr><td>{row_num}</td>{''.join([self.td(e,c=shades[i%2]) for i,e in enumerate(row)])}</tr>"
    def col_header(self, col_names):
        return f"<thead><tr>{''.join(['<th>ROW</th>']+[(f'<th>{e}</th>') for e in col_names])}</tr></thead>"
    def table(self, header, content):
        return f"<table>{''.join([self.col_header(header)]+[self.tr(row,i) for i,row in enumerate(content)])}</table>"

class HtmlCode:
    def __init__(self, code, language='raw'):
        self.html = f"""<html>
        <script src="https://cdn.jsdelivr.net/gh/google/code-prettify@master/loader/run_prettify.js?lang=json&amp;skin=sons-of-obsidian"></script>
            <pre class="prettyprint linenums">{code}</pre>
        </html>"""