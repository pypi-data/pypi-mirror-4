# -*- coding: utf-8 -*-
"""
API   [method]  Perform an arbitrary http api call

"""
import requests
import json
import logging 

#lytics
import config

log = logging.getLogger("lytics.api")


FORM = 'application/x-www-form-urlencoded; charset=utf-8'
JSON = 'application/json; charset=utf-8'
DEFAULT_UA = 'lytics-cli/0.1' 


def build_url(path):
    "Build a url"
    url = "%s/api/%s"  % (config.options.api, path)
    if not "?" in path:
        url = url + "?"
    else:
        url = url + "&"
    return "%skey=%s" % (url, config.options.key)


def doapi(url, data={}, params={}, headers={}, method = "GET"):
    """
    create an api request
    """
    implicit_headers = {
        'User-Agent': DEFAULT_UA
    }

    implicit_headers['Accept'] = 'application/json'
    implicit_headers['Content-Type'] = JSON

    if isinstance(data, dict) or isinstance(data,list):
        if len(data) > 0:
            data = json.dumps(data)
        else:
            data = ''

    for name, value in implicit_headers.items():
        if name not in headers:
            headers[name] = value

    if not "http" in url:
        url = "http://" + url

    kwargs = {
        'method': method.lower(),
        'url': url,
        'headers': headers,
        'data': data,
        'allow_redirects': True,
        'params': params,
    }
    return requests.request(**kwargs)
