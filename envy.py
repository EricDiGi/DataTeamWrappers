import os, sys
from re import sub

def snake_case(s):
  return '_'.join(
    sub('([A-Z][a-z]+)', r' \1',
    sub('([A-Z]+)', r' \1',
    s.replace('-', ' '))).split()).lower()

def load_dotenv(path=None):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                k,v = line.strip().split('=')
                os.environ[k] = v
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

# format_ = {
#     "is_json": re.match(r'^.*\.json$',file,re.IGNORECASE) and os.path.isfile(file),
#     "is_env": re.match(r'^.*\.env$',file,re.IGNORECASE) and os.path.isfile(file)
# }
# open_secrets = {
#     "is_json": lambda x: self.json.load(open(x)),
#     "is_env": lambda x: self.load_dotenv(x)
# }