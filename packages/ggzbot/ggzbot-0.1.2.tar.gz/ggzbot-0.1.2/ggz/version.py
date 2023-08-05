# jsb/version.py
#
#

""" version related stuff. """

## jsb imports

from ggz.lib.config import getmainconfig

## basic imports

import os
import binascii

## defines

version = "0.1.2"
__version__ = version

## getversion function

def getversion(txt=""):
    """ return a version string. """
    return "GGZBOT version %s DEVELOPMENT %s" % (version, txt)
