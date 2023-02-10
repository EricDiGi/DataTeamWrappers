import os, sys
import re
import json

def snake_case(s):
  if re.search(r'^[a-z][a-z\d_]*$',s.lower()):
    return s.lower()
  return '_'.join(
    re.sub('([A-Z][a-z]+)', r' \1',
    re.sub('([A-Z]+)', r' \1',
    s.replace('-', ' '))).split()).lower()

def load_dotenv(path=None):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                k,v = line.strip().split('=')
                os.environ[k] = v
        return True
    else:
        raise FileNotFoundError(path)

def env_to_dict(path=None, to_snake_case=False):
    loaded_env = {}
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                k,v = line.strip().split('=')
                if to_snake_case:
                    k = snake_case(k)
                loaded_env[k] = v
    else:
        raise FileNotFoundError(path)
    return loaded_env

def arbiter(path, to_snake_case=False):
    format_ = {
        "is_json": re.match(r'^.*\.json$',path,re.IGNORECASE) and os.path.isfile(path),
        "is_env": re.match(r'^.*\.env$',path,re.IGNORECASE) and os.path.isfile(path)
    }
    open_secrets = {
        "is_json": lambda x: json.load(open(x)),
        "is_env": lambda x: load_dotenv(x)
    }
    keys_match = len(list(set(format_.keys()).difference(set(open_secrets.keys())))) == 0
    if not keys_match:
        raise ValueError(f"Key missing from dictionary: {list(set(format_.keys()).difference(set(open_secrets.keys())))}")
    
    keys__ = list(format_.keys())

    for key in keys__:
        if format_[key]:
            opened = open_secrets[key](path)
            if opened is not None:
                return opened