# jsb/utils/log.py
#
#

""" log module. """

## jsb import

from ggz.lib.datadir import getdatadir

## basic imports

import logging
import logging.handlers
import os
import os.path
import getpass

## defines

ERASE_LINE = '\033[2K'
BOLD='\033[1m'
RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
ENDC = '\033[0m'


LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'warn': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL
         }

RLEVELS = {logging.DEBUG: 'debug',
           logging.INFO: 'info',
           logging.WARNING: 'warn',
           logging.ERROR: 'error',
           logging.CRITICAL: 'critical'
          }

def init(d):
    LOGDIR = "ggz-botlogs" # BHJTW change this for debian

    try:
        ddir = os.sep.join(LOGDIR.split(os.sep)[:-1])
        if not os.path.isdir(ddir): os.mkdir(ddir)
    except: pass

    try:
        if not os.path.isdir(LOGDIR): os.mkdir(LOGDIR)
    except: pass
    return LOGDIR

## setloglevel function

def setloglevel(level_name="warn", colors=True, datadir=None):
    """ set loglevel to level_name. """
    if not level_name: return
    LOGDIR = init(datadir or getdatadir())
    format_short = "\033[1m%(asctime)s\033[0m -=- %(levelname)-8s -=- \033[93m%(message)-75s\033[0m -=- \033[92m%(module)s.%(funcName)s.%(lineno)s\033[0m -=- \033[94m%(threadName)s\033[0m"
    format_short_plain = "%(asctime)s -=- %(levelname)-8s -=- %(message)-75s -=- %(module)s.%(funcName)s.%(lineno)s -=- %(threadName)s"
    datefmt = '%H:%M:%S'
    formatter_short = logging.Formatter(format_short, datefmt=datefmt)
    formatter_short_plain = logging.Formatter(format_short_plain, datefmt=datefmt)
    try:
        filehandler = logging.handlers.TimedRotatingFileHandler(LOGDIR + os.sep + "ggz.log", 'midnight')
    except (IOError, AttributeError) as ex:
        logging.error("can't create file loggger %s" % str(ex))
        filehandler = None
    docolors = colors or False
    level = LEVELS.get(str(level_name).lower(), logging.NOTSET)
    root = logging.getLogger()
    root.setLevel(level)
    if root and root.handlers:
        for handler in root.handlers: root.removeHandler(handler)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    if True:
         if docolors: ch.setFormatter(formatter_short)
         else: ch.setFormatter(formatter_short_plain)
         if filehandler: filehandler.setFormatter(formatter_short_plain)
    root.addHandler(ch)
    if filehandler: root.addHandler(filehandler)
    logging.warn("loglevel is %s (%s)" % (str(level), level_name))

def getloglevel():
    import logging
    root = logging.getLogger()
    return RLEVELS.get(root.level)
