# fbf/__init__.py
#
#

""" get/set globals. """

from fbf.utils.lazydict import LazyDict

altar = LazyDict()
altar.errors = LazyDict()
altar.testerrors = LazyDict()

def setglobal(name, object):
    global altar
    altar[name] = object

def getglobal(name):
    try: return altar[name]
    except KeyError: return 
