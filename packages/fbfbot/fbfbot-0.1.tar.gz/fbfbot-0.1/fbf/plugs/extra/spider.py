# fbf/plugs/common/spider.py
#
#


""" 
    Spider plugin.. Spider websites and makes an index into them.

    taken from http://code.activestate.com/recipes/576551-simple-web-crawler/

    -- BHJTW 15-11-2011 Adapted for JSONBOT
    -- BHJTW 14-09-2012 ported to FBFBOT

"""

__version__ = "0.2"
__copyright__ = "CopyRight (C) 2008-2011 by James Mills"
__license__ = "MIT"
__author__ = "James Mills"
__author_email__ = "James Mills, James dot Mills st dotred dot com dot au"
__coauthor__ = "adapted for JSONBOT,FBFBOT by Bart Thate <feedbackloop@gmail.com>"

## fbf imports

from fbf.utils.name import stripname
from fbf.utils.exception import handle_exception
from fbf.utils.urldata import UrlData
from fbf.utils.generic import waitforqueue
from fbf.utils.url import geturl2, striphtml, Url
from fbf.lib.datadir import getdatadir
from fbf.lib.persist import PersistCollection
from fbf.lib.commands import cmnds
from fbf.lib.examples import examples
from fbf.lib.threadloop import ThreadLoop
from fbf.lib.callbacks import callbacks
from fbf.imports import getBeautifulSoup
soup = getBeautifulSoup()

## basic imports

from collections import deque 
import os
import logging
import re
import sys
import time
import math
import urllib.request, urllib.error, urllib.parse
import urllib.parse
import optparse
from cgi import escape
from traceback import format_exc
from queue import Queue, Empty as QueueEmpty

## defines

running = []

## Spider class

class Spider(ThreadLoop):

    def __init__(self, url, skip=True):
        self.url = Url(url)
        self.errors = []
        self.urls = []
        self.followed = []
        self.skip = skip
        ThreadLoop.__init__(self)
        self.sTime = time.time()
        self.eTime = 0
        self.tTime = 0

    def handle(self, event, url, depth, speed=5):
        if depth < 0: return
        if not self.url.base in url: logging.warn("skipping %s (%s)" % (url, self.url.base)) ; return
        if url in self.errors: logging.warn("skipping %s" % url) ; return
        urls = []
        linknr = 0
        follownr = 0
        n = 0
        try:
            if url not in self.urls:
                self.urls.append(url)
                page = Url(url)
                time.sleep(10-speed)
                content = page.fetch()
                event.reply("fetched %s - %s - %s" % (url, len(content), content.status))
                try:
                    urldata = UrlData(url, striphtml(content))
                    if urldata.data.txt: urldata.save()
                except Exception as ex: handle_exception()
                for p in page.geturls():
                    if not p in self.errors:
                        self.put(6, event, p, depth-1, speed-1)
            if not self.queue.qsize(): self.stop()
        except Exception as e:
            logging.warn("ERROR: Can't process url '%s' (%s)" % (url, e))
            self.errors.append(url)
            handle_exception()
            if len(self.errors) > 10: self.stop()

def handle_spider(bot, event):
    if not event.args: event.missing("<url> [<depth>]") ; return
    url = event.args[0]
    try: depth = int(event.args[1])
    except ValueError: event.reply("depth need to be an integer") ; return 
    except IndexError: depth = 3
    spider = Spider(url)
    if not spider in running: running.append(spider)
    thr = spider.start()
    event.reply("calling fetcher on %s" % time.ctime(spider.sTime))
    spider.put(5, event, url, depth, 9)
    
cmnds.add("spider", handle_spider, "OPER", threaded="backend")
examples.add("spider", "run the spider on a site.", "spider http:///docs/fbfbot/handbook")

def handle_spiderstop(bot, event):
    r = len(running)
    for spider in running: spider.stop()
    event.reply("stopped %s spiders" % r)
    
cmnds.add("spider-stop", handle_spiderstop, "OPER")
examples.add("spider-stop", "stop running spiders", "spider-stop")
