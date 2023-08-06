# -*- coding: utf-8 -*-
import sys
import json
import datetime
import time 
import random
import urllib
import os 
import logging
#from argparse import FileType, OPTIONAL, ZERO_OR_MORE, SUPPRESS
import requests
from colorama import init as coloramainit
from termcolor import colored

import config
import csvupload
import query
import collect 
import httpapi
import users 
import account 

import httpiecolor
from httpapi import build_url
from pretty import pprint_table


log = logging.getLogger("lytics")
APIAGENT = "LioCLI"
BATCH_SIZE = 50

coloramainit()

modules = {"query":query,"csv":csvupload,"api":httpapi,
    "collect":collect,"users":users, "account":account}



def get_doc(method=None):
    "Get doc for a specific module or all"
    args = [arg for arg in sys.argv[1:] if arg not in ["--help","help"]]
    if len(args) == 1:
        method = args[0]
    #print("IN GET_DOC method=%s args=%s" %(method, args))
    if not method:
        return '\n'.join([modules[n].__doc__ for n in modules.keys()])
    else:
        if type(method) == list:
            if len(method) == 1:
                method = method[0]
            else:
                method = "invalid"
        if method in modules:
            return modules[method].__doc__.strip()
    return ""

def _(text):
    """Normalize whitespace."""
    return ' '.join(text.strip().split())

class LioCommands(object):

    def __init__(self, args):
        "init"
        config.options.load(args)  # config.options = config.LioOptions(args)
        self.args = args 

    def _error(self,msg):
        print("lytics error:  %s" % msg)

    def _arg(self,pos):
        if type(self.args.args) == list:
            if len(self.args.args) > pos:
                #log.debug(self.args.args)
                return self.args.args[pos]
        return ""

    def valid(self, argsreq=0):
        if len(self.args.api) < 2:
            self._error("Requires Api and is missing")
            return False
        if len(self.args.key) < 10:
            self._error("Requires apikey and is missing")
            return False
        if argsreq > 0:
            if len(self.args.args) < argsreq:
                doc = get_doc(self.args.method)
                self._error("%s requires additional arg and is missing\n\n%s" % (
                    self.args.method, doc))
                return False
        return True

    def api(self):
        """call arbitrary api
        """
        if not self.valid():
            return
        url = self._arg(0)
        if len(url) < 1:
            log.error("Requires url arg:    lytics api account  [user,account,query,meta etc]")
            return
        url = build_url(url)
        log.debug(url)
        httpiecolor.console_response(httpapi.doapi(url))

    def user(self):
        """
        Get list of Users or a specific one
        """
        if not self.valid(0):
            return
        method = self._arg(0).lower()

        if method == "list" or method == "":
            users.list(self)
        elif method == "create":
            users.create(self)

    def account(self):
        """
        actions for account
        """
        if not self.valid(0):
            return
        method = self._arg(0).lower()

        if method == "list" or method == "":
            account.list(self)
        elif method == "create":
            account.create(self)


    def query(self):
        """Query Ops"""
        if not self.valid(1):
            return
        method = self._arg(0)
        if method == "sync":
            query.sync(self)
        elif method == "list":
            query.list(self)

    def csv(self):
        """
        Read a csv file and upload to lytics:
        """
        if not self.valid(0):
            return
        csvupload.csvupload(self)

    def env(self):
        "Show the config settings"
        print(config.options.help())

    def sendjson(self,rawdata, method="GET"):
        """
        sends the data to collection servers via http
        """
        #log.debug("HERE %s" % rawdata)
        aid = self.args.aid 
        if len(aid) == 0:
            aid = self.args.key

        url = self.args.api +"/c/%s" % (aid)
        if len(self.args.stream) > 0:
            url = self.args.api +"/c/%s/%s" % (aid, self.args.stream)

        log.debug("URL1  method=%s  url==%s" % (method, url))
        if self.args.preview:
            print("would have sent %s data=\n%s" % (url, rawdata))
            return 
        if self.args.format == 'json':
            httpiecolor.console_response(httpapi.doapi(url, data=rawdata, method=method))
        else:
            httpiecolor.console_response(httpapi.doapi(url, data=rawdata, method=method))
        #print response
    
    def collect(self):
        """posts arbitrary data for collection"""
        if not self.valid(0):
            return
        collect.stdin(self)
    














































