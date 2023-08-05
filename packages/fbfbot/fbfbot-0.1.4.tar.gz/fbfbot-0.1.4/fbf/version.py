# fbf/version.py
#
#

""" version related stuff. """

## fbf imports

from fbf.lib.config import getmainconfig

## basic imports

import os
import binascii

## defines

version = "0.1.4"
__version__ = version

## getversion function

def getversion(txt=""):
    """ return a version string. """
    return "FBFBOT version %s DEVELOPMENT %s" % (version, txt)
