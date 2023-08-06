#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is the file for defining options on cli as 
well as the main entry point 
"""
import os
import sys
import logging
from . import __doc__
from . import __version__ as version
from argparse import FileType, OPTIONAL, ZERO_OR_MORE, SUPPRESS
from argparse import ArgumentParser, RawDescriptionHelpFormatter

#from .lio import main
from .lio import LioCommands, _, get_doc
from .config import enable_pretty_logging


logging.basicConfig()

log = logging.getLogger("lytics")



class Parser(ArgumentParser):
    """customize arg parse

    Handle Args, Files (stdin/out), applies defaults/validation
    """

    def __init__(self, *args, **kwargs):
        kwargs['add_help'] = False
        super(Parser, self).__init__(*args, **kwargs)

    #noinspection PyMethodOverriding
    def parse_args(self, args=None, namespace=None):
        #self.env = env

        args = super(Parser, self).parse_args(args, namespace)

        #if not args.json and env.config.implicit_content_type == 'form':
        #    args.form = True
        return args





parser = Parser(
    description="%s\n%s" % (__doc__.strip(), get_doc()) ,
    formatter_class=RawDescriptionHelpFormatter,
    epilog=_('''
        Suggestions and bug reports are greatly appreciated:
        https://github.com/lytics/lyticscli
    ''')
)

###############################################################################
# Methods & their arguments.
###############################################################################

# http://stackoverflow.com/questions/642648/how-do-i-format-positional-argument-help-using-pythons-optparse?rq=1
#http://docs.python.org/2/library/textwrap.html

methods = parser.add_argument_group()
methods.add_argument('method', metavar='',nargs=1, default=None)
methods.add_argument('args', metavar='',nargs=ZERO_OR_MORE,default=None)

###############################################################################
# Account Args
###############################################################################

account = parser.add_argument_group(title='Account Info')

account.add_argument(
    '--aid', type=str, default="",
    help='''
        Account Id (can be your "fid" you assigned at creation or our
        Lytics assigned Acocunt Id)
    '''
)
account.add_argument(
    '--key', type=str, default="",
    help=_('''
        The Lytics Access Token for authentication
    ''')
)
account.add_argument(
    '--config', type=str, default=".lytics",
    help=_('''
        The Lytics Configuration file
    ''')
)
account.add_argument(
    '--stream', type=str, default="",
    help=_('''
        The Lytics `Stream` to store/analyze this data
    ''')
)


###############################################################################
# Database Args
###############################################################################

database = parser.add_argument_group(title='Database Extraction Info')

database.add_argument(
    '--db', type=str, default="",
    help='''
        Database Name to connect to
    '''
)
database.add_argument(
    '--dbhost', type=str, default="",
    help=_('''
        The database host
    ''')
)

database.add_argument(
    '--dbuser', type=str, default="",
    help=_('''
        The database user
    ''')
)

database.add_argument(
    '--dbpwd', type=str, default="",
    help=_('''
        The database password
    ''')
)


###############################################################################
# tools
###############################################################################

clitools = parser.add_argument_group(title='Troubleshooting')

clitools.add_argument(
    '--help',
    action='help', default=SUPPRESS,
    help='Show this help message and exit'
)
clitools.add_argument('--version', action='version', version=version)
clitools.add_argument(
    '--traceback', action='store_true', default=False,
    help='Prints exception traceback should one occur.'
)
clitools.add_argument(
    '--debug', action='store_true', default=False,
    help=_('''
        Prints exception traceback should one occur, and also other
        information that is useful for debugging HTTPie itself and
        for bug reports.
    ''')
)
clitools.add_argument(
    '--api', type=str, default="https://api.lytics.io",
    help=_('''
        The Lytics api endpoint
    ''')
)
clitools.add_argument(
    '--format', type=str, default="",
    help=_('''
        The format, default is custom format, the other option is json
    ''')
)
clitools.add_argument(
    '--preview', action='store_true', default=False,
    help=_('''
        For mutation's (deletes,puts,posts) you can preview 
        what is about to happen without running it
    ''')
)

def print_debug_info(env=None):
    sys.stderr.writelines([
        'Lytics %s\n' % version,
        'Python %s %s\n' % (sys.version, sys.platform)
    ])



def main(sysargs=sys.argv[1:]):
    """Run the main program and write the output to stdout

    """
    debug = '--debug' in sysargs
    traceback = debug or '--traceback' in sysargs
    if "LIOENV" in os.environ:
        debug = True
        traceback = True

    if debug:
        enable_pretty_logging("debug")
    else:
        enable_pretty_logging("info")

    def error(msg, *args):
        msg = msg % args
        sys.stderr.write('\nlytics: error: %s\n' % msg)
    try:
        args = parser.parse_args(args=sysargs)
        cl = LioCommands(args)
        method = cl.args.method
        
        
        log.debug("METHOD = %s  ARGS=%s" % (method, args.args))
        if not hasattr(cl,method):
            parser.print_help()
        else:
            getattr(cl,method)()
        
    except (KeyboardInterrupt, SystemExit):
        if traceback:
            raise
        sys.stderr.write('\n')
    except Exception as e:
        if traceback:
            raise
        error('%s: %s', type(e).__name__, str(e))


if __name__ == '__main__':
    sys.exit(main())
