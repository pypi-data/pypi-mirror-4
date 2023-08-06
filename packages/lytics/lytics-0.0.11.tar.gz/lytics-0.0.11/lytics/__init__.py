# -*- coding: utf-8 -*-
"""
lytics Data Tools (import, data extraction, sync schema)

METHODS
==========================================================
"""
import signal, logging 

__version__ = '0.0.11'
APIAGENT = "Lytics CLI %s" % __version__

_signames = dict((getattr(signal, signame), signame) \
                    for signame in dir(signal) \
                    if signame.startswith('SIG') and '_' not in signame)

def signal_name(signum):
    try:
        return _signames[signum]
    except KeyError:
        return 'SIG_UNKNOWN'