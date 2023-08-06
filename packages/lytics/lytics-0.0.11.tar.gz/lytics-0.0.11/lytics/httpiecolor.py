# -*- coding: utf-8 -*-
"""
This module makes use of httpie for colorizing http requests
"""
import sys
import errno
import logging

import requests
from requests.compat import str, is_py3
from httpie import __version__ as httpie_version
from requests import __version__ as requests_version
from pygments import __version__ as pygments_version

from httpie.cli import parser
from httpie.client import get_response
from httpie.models import Environment
from httpie.output import build_output_stream, write, write_with_colors_win_p3k


log = logging.getLogger("lytics")


def console_response(response):
    """Use httpie to coloize output to console"""

    args=[response.request.url]
    env=Environment()

    debug = False
    traceback = False
    args = parser.parse_args(args=args, env=env)

    write_kwargs = {
        'stream': build_output_stream(args, env,
                                      response.request,
                                      response),
        'outfile': env.stdout,
        'flush': env.stdout_isatty 
    }
    try:
        if env.is_windows and is_py3:
            write_with_colors_win_p3k(**write_kwargs)
        else:
            write(**write_kwargs)

    except IOError as e:
        if not traceback and e.errno == errno.EPIPE:
            # Ignore broken pipes unless --traceback.
            log.error('\n')
        else:
            raise

