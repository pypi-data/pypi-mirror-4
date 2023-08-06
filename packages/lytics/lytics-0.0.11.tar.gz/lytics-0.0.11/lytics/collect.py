# -*- coding: utf-8 -*-
"""

COLLECT    collect data and send to lytics
----------------------------------------------------
usage:
    
    # pipe data to collector via stdout
    myyapp > lytics collect 

    # read data from stdin 
    lytics collect   

    lytics collect < /path/to/file.json 


"""
import sys, json, datetime, time, os, logging
import requests
from tornado.httpclient import HTTPClient

from config import options
from .input import InputHelper
from lytics import APIAGENT

BATCH_SIZE = 50

log = logging.getLogger("lytics")


def stdin(cli):
    http = HTTPClient()
    jsondata = None
    line = ""
    data = None
    stream = ""
    if len(options.stream) > 0:
        stream = "/" + options.stream
    url = options.api  + "/c/%s%s?key=%s" % (options.aid, stream, options.key)
    log.debug(url)
    # for each line from stdin
    while 1:
        try:
            line = sys.stdin.readline()
        except KeyboardInterrupt:
            break

        if not line:
            break
        """
        TODO 
            - batching 
            - async 
        """
        jsondata = None
        line = line.strip()
        # note we aren't really worried about encoding, formatting here
        data = line
        log.debug("SENDING '%s'" % (data))
        response = http.fetch(url, 
            method="POST", body=data, headers={'user-agent':APIAGENT},
            request_timeout=60,connect_timeout=60)



