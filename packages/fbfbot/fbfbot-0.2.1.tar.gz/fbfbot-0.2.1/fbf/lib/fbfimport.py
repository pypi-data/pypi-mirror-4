# fbf/lib/fbfimport.py
#
#

""" use the imp module to import modules. """

## basic imports

import time
import sys
import imp
import os
import _thread
import logging

## _import function

def _import(name):
    """ do a import (full). """
    logging.debug("importing %s" % name)
    if not name: raise Exception(name)
    mods = []
    mm = ""
    res = None
    for m in name.split('.'):
        mm += m
        mm += "."
        res = __import__(mm)
    return sys.modules[name]


def silent_import(name):
    from fbf.utils.exception import exceptionmsg
    try: return _import(name)
    except Exception as ex: logging.error(exceptionmsg())

## force_import function

def force_import(name):
    """ force import of module <name> by replacing it in sys.modules. """
    try: del sys.modules[name]
    except KeyError: pass
    plug = __import(name)
    return plug

def import_byfile(modname, filename):
    try: return imp.load_source(modname, filename)
    except NotImplementedError: return myimport(filename[:-3].replace(os.sep, "."))

