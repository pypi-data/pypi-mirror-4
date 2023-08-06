# -*- coding: utf-8 -*-
"""

USER            Administrative User management 
----------------------------------------------------
usage:

                lytics user name@email
                lytics user
                lytics user create 

USER  list      Get list of users

USER  [id]      Get info on specific user
                
USER  create    Create a new user 
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
    Create A New user
    """
    url = build_url("user")
    user = {}
    user['email'] = raw_input('What is their email: ')
    user['name'] = raw_input('What is their full name?: ')
    auth = raw_input('How will they logon?  [google,github,password] (default = google): ')
    if auth == "google" or auth == "":
        pass
    if auth == "google":
        needsEmail = False
        if "email" not in user:
            needsEmail = True
        elif len(user["email"]) < 4:
            needsEmail = True
        if needsEmail:
            user['email'] =raw_input("To use google login requires google email: ")
    if auth == "password":
        user['password'] = raw_input('Password? ')
    if cli.args.preview:
        print("would have sent %s data=\n%s" % (url, user))
        return 
    log.debug(user)
    resp = httpapi.doapi(url, data=user, method="POST")
    httpiecolor.console_response(resp)


def list(cli):
    """
    Get list of Users or a specific one
    """
    uid = cli._arg(0)
    url = "" 
    if len(uid) == 0 :
        url = build_url("user")
    else:
        url = build_url("user/" + uid)
    log.debug(url)
    if cli.args.format == 'json':
        httpiecolor.console_response(httpapi.doapi(url))
    else:
        resp = httpapi.doapi(url)
        if resp.status_code < 400:
            data = json.loads(resp.text)
            out = [['Name', "Email","Roles"]]
            if "data" in data:
                if isinstance(data["data"],dict):
                    httpiecolor.console_response(resp)
                else:
                    for u in data["data"]:
                        roles = ""
                        if "roles" in u and type(u["roles"]) == type([]):
                            roles = ",".join(u['roles'])
                        out.append([u["name"],u["email"],roles])
                    print("")
                    pprint_table(sys.stdout,out)