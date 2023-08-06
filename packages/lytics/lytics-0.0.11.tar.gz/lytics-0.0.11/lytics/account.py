# -*- coding: utf-8 -*-
"""

ACCOUNT            Administrative Account management 
----------------------------------------------------
usage:

                lytics account  name
                lytics account
                lytics account create 

ACCOUNT  list      Get list of accounts

ACCOUNT  [id]      Get info on specific account
                
ACCOUNT  create    Create a new account 
"""
import sys
import requests
import json
import logging 
import httpapi
import httpiecolor
from httpapi import build_url
from pretty import pprint_table

log = logging.getLogger("lytics")


def create(cli):
    """
    Create A New account
    """
    data = {}
    data['fid'] = raw_input('What is the unique id for this account?: ')
    data['name'] = raw_input('What is the name of this account?: ')
    log.debug(data)
    resp = httpapi.doapi(build_url("account"), data=data, method="POST")
    httpiecolor.console_response(resp)


def list(cli):
    """
    Get list of accounts or a specific one
    """
    uid = cli._arg(0)
    url = "" 
    if len(uid) == 0 :
        url = build_url("account")
    else:
        url = build_url("account/" + uid)
    log.debug(url)
    if cli.args.format == 'json':
        httpiecolor.console_response(httpapi.doapi(url))
    else:
        resp = httpapi.doapi(url)
        if resp.status_code < 400:
            data = json.loads(resp.text)
            out = [['Name', "YourId","Account ID","apikey"]]
            if "data" in data:
                if isinstance(data["data"],dict):
                    httpiecolor.console_response(resp)
                else:
                    for u in data["data"]:
                        out.append([u["name"],u["fid"],u["aid"],u["apikey"]])
                    print("")
                    pprint_table(sys.stdout,out)