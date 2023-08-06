# -*- coding: utf-8 -*-
"""
CSV   [file]    Read a csv file and upload to lytics
----------------------------------------------------

                lytics csv < /path/to/file.csv

                # optional stream name
                lytics --stream=streamName csv < /path/to/file.csv 

"""
import sys, json, datetime, time, urllib, os, logging, csv
import requests
from config import options, BATCH_SIZE
from .input import ReadLineIterator 

log = logging.getLogger("lytics")


def csvupload(cli):
    """
    Sync a raw text csv file
    """
    # for each line from stdin
    csvreader = csv.reader(ReadLineIterator(sys.stdin),delimiter=',')
    cols = csvreader.next()
    log.debug("cols = %s batch_size=%d" %(cols, BATCH_SIZE))
    rows = []

    for row in csvreader:
        rd, ct = {}, 0
        for col in cols:
            val = row[ct].strip()
            if len(val) > 0:
                rd[col] = val
            ct += 1
        if len(rd) > 0:
            rows.append(rd)
    
    def send_try(data):
        try:
            cli.sendjson(data,method="POST")
        except KeyboardInterrupt:
            log.debug("in keyboard interupt")
            return
        except:
            log.error("?SHIT?")

    done = False
    while not done:
        if len(rows) > BATCH_SIZE:
            data = rows[:BATCH_SIZE]
            rows = rows[BATCH_SIZE:]
            send_try(data)
        else:
            if len(rows) > 0:
                send_try(rows)
            return


 

