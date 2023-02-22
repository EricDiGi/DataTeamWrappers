import os, sys
import re
import json as js
import glob

from .flags import SNAKE_CASE

from .mode import *

def __init__():
    pass

# ROUTERS
_format_ = {
    "is_json": lambda path: re.match(r'^.*\.json$',path,re.IGNORECASE) and os.path.isfile(path),
    "is_env": lambda path: re.match(r'^.*\.env$',path,re.IGNORECASE) and os.path.isfile(path)
}
_open_resolution_ = {
    "is_json": lambda path,d,f: json(path,d,f),
    "is_env": lambda path,d,f: env(path, d,f)
}

# FLAGS

# FUNCTIONS
def find(search="", ext=".env"):
    """
    Find a file within the current user's directory.(Down from root:/user/user1/*)
    search: The string to search for.
    ext: The file extension to search for.
    
    Returns: A list of the files found.
    """
    root = os.getcwd().split(os.getlogin())[0]+os.getlogin()+"/"
    return list(filter(lambda g: ("AppData" not in g) and (search in g), glob.iglob(root+"**/*"+ext,recursive=True)))

def is_json(path):
    """Check if the path is a json file
    path: path to file
    """
    if os.path.isfile(path):
        return _format_["is_json"](path)
    return False

def is_env(path):
    """Check if the path is an environment file
    path: path to file
    """
    if os.path.isfile(path):
        return _format_["is_env"](path)
    return False

def snake_case(s):
    """Convert a string to snake case
    s: string to convert
    """
    return re.sub( r'[\- ]', '_',
        re.sub(r'([a-z])([A-Z])', r'\1_\2', s).lower()
    )

def env(path, default=True,flags=[]):
    """
    Open an environment file
    path: path to file
    default: boolean use default loading strategy if false will use the alternative (JSON)
    flags: a list of flags used during negotiation
    
    Returns: A dictionary of the negotiated solution if JSON resolution was reached, None otherwise.
    """
    out = None if default else {}
    if os.path.isfile(path):
        with open(path,'r') as f:
            for line in f:
                k,v = line.strip().split('=',1)
                if default:
                    os.environ[k] = v
                else:
                    out.update({snake_case(k) if SNAKE_CASE in flags else k:v})
        return out
    else:
        raise FileNotFoundError(path)

def json(path, default=True,flags=[]):
    """
    Open a json file
    path: path to file
    default: boolean use default loading strategy if false will use the alternative (ENV)
    flags: a list of flags used during negotiation
    
    Returns: A dictionary of the negotiated solution if JSON resolution was reached, None otherwise.
    """
    if os.path.isfile(path):
        jj = map(lambda k,v: (snake_case(k) if SNAKE_CASE in flags else k ,v), js.load(open(path,'r')).items())
        if default:
            return jj
        for k,v in jj.items():
            os.environ[k] = str(v)
    else:
        raise FileNotFoundError(path)

def arbiter(path,default=True,flags=[]):
    """Negotiates the environment loading strategy to use for a file type
    path: the path to the file to load
    default: boolean use default loading strategy (JSON,ENV) if false will use the alternative (ENV,JSON)
    flags: a list of flags to negotiate the resolution to

    Returns: A dictionary of the negotiated solution if JSON resolution was reached, None otherwise.
    """
    keys_match = len(list(set(_format_.keys()).difference(set(_open_resolution_.keys())))) == 0
    if not keys_match:
        raise ValueError(f"Key missing from dictionary: {list(set(_format_.keys()).difference(set(_open_resolution_.keys())))}")
    
    keys__ = list(_format_.keys())
    
    for key in keys__:
        if _format_[key](path):
            return _open_resolution_[key](path,default,flags)

def save(path,vars,mode):
    """
    A method to save a specified environment using a specified mode.
    path: the path to save to
    vars: a dictionary of the variables to save. Accepts dicts or lists of tuples.
    mode: the mode to use for saving (envy.mode.*)

    Returns: None
    """
    vars = dict(vars)
    __modes__ = {
        ENV: "\n".join(list(map(lambda a: "{}={}".format(a[0].upper(), a[1]), list(vars.items())))),
        JSON: js.dumps(vars)
    }
    with open(path,'w') as f:
        f.write(__modes__[mode])

__all__ = [
    "find",
    "is_json",
    "is_env",
    "arbiter",
    "save"
]