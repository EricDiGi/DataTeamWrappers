"""
A module built to simplify interactions with Domo datasets.
"""

import os
import json
from IPython.display import display

try:
    from pydomo import Domo
except Exception as e:
    raise ModuleNotFoundError("PyDomo not found: please try running \"pip install pydomo\"") from e

# %%
def _raise(err):
    raise err

def load_env(envpath):
    """Similar to dotenv.load_env but doesn't require import"""
    with open(envpath, encoding='UTF-8') as env:
        for line in env:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=')
                os.environ[key] = value

class DomoMeido:
    """
        A class representing a connection to Domo
    """
    connected = False
    template_loaded = False
    def __init__(self, env_file=None, utility_file=None, table_def=None):

        self.has_raw_json = ((table_def is not None) and isinstance(table_def,(dict,list)))
        if self.has_raw_json:
            self.raw_json = table_def if isinstance(table_def, list) else [table_def]
        elif (table_def is not None) and isinstance(table_def, str):
            self.has_raw_json = True
            self.raw_json = json.loads(table_def)

        self.utility_file = utility_file
        self.get_enviroment(env_file)

        self.domo = None
        self.init_domo()

        self.template = None
        self.open_template()

    def get_enviroment(self, env):
        """Load environment variables from file into OS environment"""
        if env:
            load_env(env)
        else:
            raise Exception('Please specify a valid environment file')
    def init_domo(self, host='api.domo.com'):
        """Initialize the Domo connection"""
        try:
            self.domo = Domo(os.environ['CLIENT_ID'], os.environ['CLIENT_SECRET'], api_host=host)
            self.connected = True
        except Exception as exc:
            raise Exception("Unable to connect to domo") from exc
    def open_template(self):
        """Unpack the template json"""
        if self.has_raw_json:
            self.template = self.raw_json
            self.template_loaded = True
            return
        try:
            with open(self.utility_file, encoding='UTF-8') as json_file:
                self.template = json.load(json_file)
            self.template_loaded = True
        except Exception as exc:
            self.template_loaded = False
            raise Exception("Unable to open template file") from exc
    def status(self):
        """Return the status of the Domo connection"""
        return (
            f"Domo is {0} and your template is {1}".format(
                ("connected" if self.connected else "not connected"),
                ("loaded" if self.template_loaded else "not loaded")
            )
        )
    def query(self,table):
        """Specify the query for Domo to implement using the specifications found in the template"""
        cols=','.join(table.columns)
        limit=table.limit
        lim = f"limit {limit}" if table.limit is not None else ""
        return f"select {cols} from table {lim}"
    def domo_query(self,table):
        """Run the query and return a dataframe."""
        return self.domo.ds_query(table.id, self.query(table))
    def load(self):
        """Load all tables specified in the template into Table objects"""
        dataset = DomoSet()
        names = [table["name"] for table in self.template]
        for i,table in enumerate(self.template):
            dataset[names[i]] = DomoTable(table)
            dataset[names[i]].dataframe = self.domo_query(dataset[names[i]])
        return dataset
# %%
class DomoTable():
    """
        A class representing a table in Domo
    """
    def __init__(self, table_dict):
        if table_dict.get("id") is not None:
            self.id = table_dict["id"]
        else:
            _raise(Exception("Table requires a unique id to work"))
        if table_dict.get("name") is not None:
            self.name = table_dict["name"]
        else:
            _raise(Exception("Table does not have a name"))
        self.desc = table_dict["description"] if table_dict.get("description") is not None else None
        self.columns = table_dict["columns"] if table_dict.get("columns") is not None else ["*"]
        self.limit = table_dict["limit"] if table_dict.get("limit") is not None else None
        self.dataframe = None
    def close(self):
        """Deconstructor"""
        del self
    def attr(self):
        """Return the attributes of the Table"""
        return self.__dict__
    def __repr__(self):
        display(self.dataframe)
        return ""
# %%
class DomoSet():
    """An abstract class to simplify dynamic attribute naming"""
    def __init__(self):
        pass
    def __setitem__(self, key, value):
        setattr(self, key, value)
    def __getitem__(self, key):
        return getattr(self, key)
    def keys(self):
        return list(self.__dict__.keys())
