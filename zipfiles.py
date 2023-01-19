
import os, sys
import re

class zipfiles(object):
    packages = ["zipfile","glob"]

    def __init__(self):
        self.safeImport(self.packages)
        self.cwd = os.getcwd()
        self.files = []
    
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
        
    def findall(self, dir: str) -> list:
        os.chdir(dir)
        self.files = self.glob.glob("*.zip")
        os.chdir(self.cwd)
        return self.files

    def unzip(self, files, to=None):
      if to == None:
        raise FileNotFoundError("A Directory must be specified before unzipping the file - Point to a location from the current directory i.e. \'./A/B/C\'")
      for f in files:
        with self.zipfile.ZipFile(f,"r") as zip:
            zip.extractall(path=to)

class Zipper(str):
  # TODO enable recursion to unzip inplace
  def unzip(self, del_zips=False): 
    zip = zipfiles()
    files = zip.findall(self)
    for f in files:
      zip.unzip([self+"/"+f],to=self+"/"+'/'.join(f.split('/')[:-1]))
      if del_zips:
        os.remove(self+"/"+f)
