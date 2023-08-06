# -*- coding: utf-8 -*-
"""
This reads/writes a bash compatible .lytics config file to the local 
directory, which allows settings to be stored persistently, as well
as allow usage for bash scripts
"""
import sys, os, logging
import ConfigParser

log = logging.getLogger("lytics")

conf_file = None
config_lines = []
BATCH_SIZE = 50


class LioOptions(object):
    
    def load(self,args):
        if type(args.method) == list and len(args.method) == 1:
            args.method = args.method[0].lower()
        self.args = args 
        getEnv()

    def __getattr__(self,name):
        if name in self.args:
            #print("Getattr %s: %s" % (name, getattr(self.args,name)))
            return getattr(self.args,name)
        return ""

    def setval(self,name,val):
        self.args.__setattr__(name,val)

    def help(self):
        out = """
        aid=%s
        key=%s
        api=%s
        """ % (self.aid, self.key, self.api)
        return out

options = LioOptions()


def enable_pretty_logging(level):
    """Turns on pretty logging"""
    
    log.setLevel(getattr(logging, level.upper()))

def getEnv():
    """
    Load LIOKEY, LIOAID,LIOAPI env variables if they exist

        LIOKEY = key 
        LIOAID = aid 
        LIOAPI = api 
    """
    try:
        apikey = os.environ["LIOKEY"]
        if len(apikey) > 0:
            options.args.key = apikey
    except:
        pass
    try:
        aid = os.environ["LIOAID"]
        if len(aid) > 0:
            options.args.aid = aid
    except:
        pass
    try:
        apistr = os.environ["LIOAPI"]
        if len(apistr) > 0:
            if not "http" in apistr:
                apistr = "http://" + apistr
            options.setval("api", apistr)
    except Exception as e:
        pass

