# fbf/imports.py
#
#

""" provide a import wrappers for the contrib packages. """

## lib imports

from fbf.lib.fbfimport import _import

## basic imports

import logging

## getjson function

def getjson():
    mod = _import("json")
    logging.debug("json module is %s" % str(mod))
    return mod

## getfeedparser function

def getfeedparser():
    try: mod = _import("feedparser")
    except: mod = _import("fbf.contrib.feedparser")
    logging.info("feedparser module is %s" % str(mod))
    return mod

def getoauth():
    try: mod = _import("oauth")
    except:
        mod = _import("fbf.contrib.oauth")
    logging.info("oauth module is %s" % str(mod))
    return mod

def getrequests():
    try: mod = _import("requests")
    except: mod = None
    logging.info("requests module is %s" % str(mod))
    return mod

def gettornado():
    try: mod = _import("tornado")
    except: mod = _import("fbf.contrib.tornado")
    logging.warn("tornado module is %s" % str(mod))
    return mod

def getBeautifulSoup():
    try: mod = _import("BeautifulSoup")
    except: mod = _import("fbf.contrib.bs4")
    logging.info("BeautifulSoup module is %s" % str(mod))
    return mod

def getsleek():
    try: mod = _import("sleekxmpp")
    except: mod = _import("fbf.contrib.sleekxmpp")
    logging.info("sleek module is %s" % str(mod))
    return mod
