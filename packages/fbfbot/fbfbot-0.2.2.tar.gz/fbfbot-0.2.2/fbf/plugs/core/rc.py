# fbf/plugs/core/rc.py
#
#

""" fbfbot resource files .. files with the .fbf extension which consists of commands to be executed. """

## fbf imports

from fbf.lib.commands import cmnds
from fbf.lib.examples import examples
from fbf.utils.url import geturl2
from fbf.utils.exception import handle_exception
from fbf.utils.generic import waitforqueue, waitevents
from fbf.lib.config import getmainconfig

## basic imports

import copy

## defines

cpy = copy.deepcopy

## rc command

def handle_rc(bot, event):
    """ arguments: <file>|<url> - execute a .fbf resource file with bot commands. """
    if not event.rest: event.missing("<file>|<url>") ; return
    if not getmainconfig().allowrc: event.reply("rc mode is not enabled") ; return
    teller = 0
    t = event.rest
    waiting = []
    try:
        try:
            if getmainconfig().allowremoterc and t.startswith("http"): data = geturl2(t)
            else: data = open(t, 'r').read()
        except IOError as ex: event.reply("I/O error: %s" % str(ex)) ; return
        if not data: event.reply("can't get data from %s" % event.rest) ; return
        for d in data.split("\n"):
            i = d.strip()
            if not i: continue
            if i.startswith("#"): continue
            e = cpy(event)
            e.txt = "%s" % i.strip()
            e.direct = True
            bot.put(e)
            waiting.append(e)
            teller += 1
        event.reply("%s commands executed" % teller)
    except Exception as ex: event.reply("an error occured: %s" % str(ex)) ; handle_exception()

cmnds.add("rc", handle_rc, ["OPER"], threaded=True)
examples.add("rc", "execute a file of fbfbot commands .. from file or url", "1) rc resource.fbf 2) rc http:///resource.fbf")
