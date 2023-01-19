"""Built to simplify SFTP queries"""
import os
#import sys
import re

class sftp(object):
    packages = ["pysftp","json","glob"]
    def __init__(self, secret_file=None, timeout=1200):
        self.safeImport(self.packages)

        self.secrets = self.__load_secrets__(secret_file)

        self.cnopts = self.pysftp.CnOpts()
        self.cnopts.hostkeys = None
        self.conn = self.pysftp.Connection(**self.secrets, cnopts=self.cnopts)
        self.conn.timeout = timeout

        self.cwd = os.getcwd()

    def close(self):
      self.conn.close()

    def EVERYTHING(self):
        everything = []
        empty_func_ = lambda x: None
        self.conn.walktree("", lambda path: everything.append(path), empty_func_, empty_func_, recurse=True)
        return everything
    def __setattr__(self, __name: str, __value) -> None:
        self.__dict__[__name] = __value

    def safeImport(self, packages):
        p = packages if type(packages) == str else packages[0]
        try:
            self.__setattr__(p,__import__(p))
        except ImportError:
            os.system("pip install " + p)
            self.__setattr__(p,__import__(p))
        if len(packages) > 1:
            self.safeImport(packages[1:])

    def __load_secrets__(self,file):
        format_ = {
            "is_json": re.match(r'^.*\.json$',file,re.IGNORECASE) and os.path.isfile(file),
            "is_env": re.match(r'^.*\.env$',file,re.IGNORECASE) and os.path.isfile(file)
        }
        open_secrets = {
            "is_json": lambda x: self.json.load(open(x)),
            "is_env": lambda x: self.load_dotenv(x)
        }
        secret = list(filter(None,map(lambda x: open_secrets[x](file) if format_[x]  else None, format_.keys())))[0]
        return secret
    
    # Gets a list of files from the sftp server
    def get(self, files, to="./SFTP_clone") -> None:
        cwd = os.getcwd()
        if not os.path.exists(to):
          os.makedirs(to)
          os.chdir(to)
        for f in files:
            _path = f.split("/")
            parent_path = to+'/'+'/'.join(_path[:-1])
            with self.conn.cd():
                for segment in _path[:-1]:
                    self.conn.chdir(segment)
                try:
                    self.conn.get(_path[-1])
                except Exception as e:
                    return None
        os.chdir(cwd)
        return to