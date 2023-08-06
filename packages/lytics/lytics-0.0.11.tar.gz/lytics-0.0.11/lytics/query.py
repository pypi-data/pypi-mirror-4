# -*- coding: utf-8 -*-
"""
QUERY    Operations on queries
----------------------------------------
QUERY LIST 
QUERY SYNC < file.lql    # sync lql formated file
QUERY DELETE name 

"""
import sys, json, datetime, time, os, logging
import requests
import tornado
from tornado.httpclient import HTTPClient
from colorama import init as coloramainit
from termcolor import colored

from config import options
from .input import InputHelper

log = logging.getLogger("lytics")

def sync(cli):
    """
    Sync queries to lytics api from raw text files of .lql type 
    It assumes each query is seperated by at least one blank line
    """
    ih = InputHelper()
    ql = ih.parse()
    url = '%s/api/query?key=%s%s' % (options.api, options.key, ih.qs)

    log.debug("Syncing %s Queries " % (len(ql)))
    
    if options.preview:
        log.warn("would have sent %s" % (url))
        for q in ql:
            print(q[0] + "\n" + q[1])
        return

    payload = []
    for q in ql:
        payload.append({'peg': q[0] + q[1], "idx":0})
        #log.info(q)

    
    log.warn("connecting to %s" % (url))
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    try:
        jsdata = json.loads(r.text)
        errors = []
        #print(json.dumps(jsdata, sort_keys=True, indent=2))
        if 'data' in jsdata:
            for qry in jsdata['data']:
                if "status" in qry and qry['status'] == "error":
                    errors.append(qry)
                elif 'peg' in qry:
                    print colored(qry['peg'] + "\n\n", 'green')
            for err in errors:
                print colored("FAILED TO PARSE\n" + qry['peg'] + "\n\n", 'red')
        else:
            print(json.dumps(jsdata, sort_keys=True, indent=2))
    except Exception, e:
        if options.traceback:
            raise
        log.error(e)
        


def list(cli):
    "Lists queries"
    url = '%s/api/query?key=%s' % (options.api, options.key)
    r = requests.get(url)
    if r.status_code < 400:
        data = json.loads(r.text)
        if 'data' in data and "queries" in data['data']:
            for qry in data["data"]['queries']:
                print colored(qry['peg'] + "\n\n", 'green')
    else:
        print url
        print("ERROR %s" % (r.text))



