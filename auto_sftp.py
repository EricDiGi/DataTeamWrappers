"""Built to simplify SFTP queries"""
import os
import sys
import re
import pysftp

REQUIRED_KEYS = ["secrets", "files", "local_directory"]
REQUIRED_SECRETS_KEYS = ["hostname", "username", "password"]

plan_template = {
    "secrets": {
        'hostname': "Some.URL.host",
        'username': "SomeUser",
        'password': "Passw0rd",
    },
    "timeout": 1200,
    "files": [
        {"path": "./*"}
    ],
    "local_directory": "./Downloads",
    "maintain_file_structure": False,
    "logging": {
        "verbose":False,
        # TODO VVV
        # "level": logging.INFO,
        # "log_file": "./somelog.log"
    }
}

class SftpClient(object):
    def __init__(self, plan):
        self.plan = plan
        self.maintain_file_structure = False

        required_keys_exist = sorted(REQUIRED_KEYS) == sorted(set(self.plan.keys()).intersection(set(REQUIRED_KEYS)))
        if not required_keys_exist:
            missing_key = set(REQUIRED_KEYS).difference(set(self.plan.keys()))
            raise KeyError(f"Missing required keys: {missing_key}")

        required_secrets_exist = sorted(REQUIRED_SECRETS_KEYS) == sorted(set(self.plan["secrets"].keys()).intersection(set(REQUIRED_SECRETS_KEYS)))
        if not required_secrets_exist:
            missing_secret = set(REQUIRED_SECRETS_KEYS).difference(set(self.plan["secrets"].keys()))
            raise KeyError(f"Missing required secrets: {missing_secret}")
        
        # Local directory
        self.local_directory = self.plan["local_directory"]
        self.cwd = os.getcwd()
        if not os.path.exists(self.local_directory):
            os.makedirs(self.local_directory)
        
        if 'maintain_file_structure' in self.plan.keys():
            self.maintain_file_structure = self.plan['maintain_file_structure']
    
    def __verbose_print__(self, output, end='\n'):
        if (("logging" in self.plan.keys()) and ("verbose" in self.plan['logging'].keys())) and self.plan['logging']["verbose"]:
            print(output, end=end)

    def __enter__(self):
        self.cnopts = pysftp.CnOpts()
        self.cnopts.hostkeys = None
        self.conn = pysftp.Connection(
            self.plan["secrets"]["hostname"],\
            username = self.plan["secrets"]["username"],\
            password = self.plan["secrets"]["password"],\
            cnopts=self.cnopts\
        )
        self.__verbose_print__(f"Connecting to \"{self.plan['secrets']['hostname']}\"")
        self.conn.timeout = self.plan["timeout"] if "timeout" in self.plan.keys() else 1200
        return self
    
    def __exit__(self,*args):
        self.__verbose_print__(f"Disconnecting from \"{self.plan['secrets']['hostname']}\"")
        os.chdir(self.cwd)
        self.conn.close()
        return None

    def get_dir_path(self, path):
        return re.sub(r'(\/\w*|\\\w*)\.\w*$','',path)

    def execute_plan(self):
        preserve_mtime = False
        if "preserve_mtime" in self.plan.keys():
            preserve_mtime = self.plan["preserve_mtime"]

        methods = {
            "copy_directory": lambda fp: self.conn.get_d(fp,'./',preserve_mtime=preserve_mtime),
            "copy_file": lambda fp: self.conn.get(fp,preserve_mtime=preserve_mtime),
            "deep_copy_directory": lambda fp: self.conn.get_r(fp,'./',preserve_mtime=preserve_mtime),
        }
        
        for task in self.plan["files"]:
            os.chdir(self.local_directory)
            if self.maintain_file_structure:
                print(f"Cloning Structure of {self.get_dir_path(task['path'])}")
                if not os.path.exists(self.get_dir_path(task['path'])):
                    os.makedirs(self.get_dir_path(task['path']))
                os.chdir(self.get_dir_path(task['path']))
            methods[task["method"]](task["path"])
            os.chdir(self.cwd+self.local_directory[1:])
            
            