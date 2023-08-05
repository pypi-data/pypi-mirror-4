#!/usr/bin/env python

from subprocess import Popen, PIPE
import os,datetime
from glob import glob

__doc__="Usage:\n>>> logger=quicklog.QuickLog('log_file_name')\n>>> logger('Here goes the message')"
__version__=1.0
__author__="Chris Anoikesis"

class QuickLog(object):
  
  get_time=lambda self: str(datetime.datetime.now()).split(".")[0]
  get_time=property(get_time)
  
  def __init__(self,name,dir=os.environ["HOME"]+"/.log/quicklog/"):
    assert name.__class__=="".__class__, "name arg has to be of a str instance."
    try:
      os.makedirs(dir)
    except OSError:
      pass #cool, the directory exists yet.
    self.filename=dir+name+".log"
    if not self.filename in glob(dir+"*"):
      open(self.filename,'w').write("#Created by QuickLog at {0}\n".format(self.get_time))
  
  def log(self,msg):
    source="{0}: {1}".format(self.get_time,msg)
    command="""echo "{0}" >> {1}\n""".format(source,self.filename)
    Popen(command,shell=True,stdout=PIPE) 
