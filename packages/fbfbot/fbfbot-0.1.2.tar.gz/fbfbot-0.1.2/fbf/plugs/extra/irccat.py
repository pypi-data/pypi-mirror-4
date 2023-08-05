#!/usr/bin/env python
"""
irccat.py - fbfbot "irccat" Module
Copyright 2011, Richard Bateman
Licensed under the New BSD License.

Written to be used in the #firebreath IRC channel: http://www.firebreath.org

To test, set up the host and port, then use something like:

echo "@taxilian I am awesome" | netcat -g0 localhost 54321

echo "#channel I am awesome" | netcat -g0 localhost 54321

you can specify multiple users (with @) and channels (with #) by seperating them
with commas.  Not that with jabber, channels tend to be treated as users
unless you set up an alias in your channel:

!irccat_add_alias #channel

BHJTW - ported to FBFBOT on 15-09-2012

"""

## fbf imports

from fbf.lib.threads import start_new_thread
from fbf.lib.persist import PlugPersist
from fbf.lib.fleet import getfleet
from fbf.lib.commands import cmnds
from fbf.lib.examples import examples
from fbf.lib.callbacks import callbacks

## basic imports

import logging
import time

## defines

cfg = PlugPersist("irccat", {
    "botnames": ["default-sxmpp",],
    "host": "localhost",
    "port": "54321",
    "aliases": {},
    "enable": False,
    })

import socketserver
from socketserver import ThreadingMixIn, StreamRequestHandler

shared_data = {}

server = None

class IrcCatListener(ThreadingMixIn, StreamRequestHandler):
    def handle(self):
        fleet = getfleet()
        msg = self.rfile.readline().strip()
        logging.warn("received %s" % msg)
        dest, msg = self.splitMsg(msg)
        for chan in dest:
            logging.info("sending to %s" % chan)
            for botname in fleet.list():
                bot = fleet.byname(botname)
                if bot:
                    if chan[0] == "#" and chan not in bot.state['joinedchannels']:
                        logging.warn("someone tried to make me say something in a channel i'm not in!")
                    else:
                        bot.say(chan, msg)
                else: logging.error("can't find %s bot in fleet" % botname)

    def splitMsg(self, message):
        if message[0] not in ('#', '@'): return [], message
        dest, message = message.split(" ", 1)
        dest = [x.strip().strip("@") for x in dest.split(",")]
        finalDest = []
        for d in dest:
            finalDest.append(d)
            if d in list(cfg.data["aliases"].keys()):
                for alias in cfg.data["aliases"][d]:
                    finalDest.append(alias)
        return finalDest, message

def dummycb(bot, event): pass

callbacks.add("START", dummycb)



def init_threaded():
    global server
    if server: logging.warn("irccat server is already running.") ; return
    if not cfg.data.enable: logging.warn("irccat is not enabled.") ; return 
    time.sleep(3)
    if "host" not in cfg.data or "port" not in cfg.data:
        cfg.data["host"] = "localhost"
        cfg.data["port"] = 54321
        cfg.data["botnames"] = ["default-sxmpp",]
        cfg.data["aliases"] = {}
    if not cfg.data.aliases: cfg.data.aliases = {}
    cfg.save()
    try:
        server = socketserver.TCPServer((cfg.data["host"], int(cfg.data["port"])), IrcCatListener)
    except Exception as ex: logging.error(str(ex)) ; return
    logging.warn("starting irccat server on %s:%s" % (cfg.data["host"], cfg.data["port"]))
    start_new_thread(server.serve_forever, ())

def shutdown():
    global server
    if server:
        logging.warn("shutting down the irccat server")
        server.shutdown()

def handle_irccat_add_alias(bot, ievent):
    if len(ievent.args) != 1:
        ievent.reply("syntax: irccat_add_alias <alias> (where <alias> is the channel you want notifications for)")
        return
    dest = ievent.args[0]
    if not cfg.data.aliases: cfg.data.aliases = {}
    if dest not in cfg.data["aliases"]:
        cfg.data["aliases"][dest] = []
    if ievent.channel not in cfg.data["aliases"][dest]:
        cfg.data["aliases"][dest].append(ievent.channel)
    cfg.save()
    ievent.reply("%s will now receive irccat messages directed at %s" % (ievent.channel, dest))
cmnds.add("irccat_add_alias", handle_irccat_add_alias, ['OPER'])
examples.add("irccat_add_alias", "add an alias to the current channel from the specified one", "irccat_add_alias #firebreath")

def handle_irccat_list_aliases(bot, ievent):
    """ List all aliases defined for the current channel """
    aliases = [dest for dest, chanlist in cfg.data["aliases"].items() if ievent.channel in chanlist]

    ievent.reply("%s is receiving irccat messages directed at: %s" % (ievent.channel, ", ".join(aliases)))
cmnds.add("irccat_list_aliases", handle_irccat_list_aliases, ['OPER'])
examples.add("irccat_list_aliases", "lists the aliases for the current channel", "irccat_list_aliases")

def handle_irccat_del_alias(bot, ievent):
    if len(ievent.args) != 1:
        ievent.reply("syntax: irccat_del_alias <alias> (where <alias> is the channel you no longer want notifications for)")
        return
    dest = ievent.args[0]
    if dest not in cfg.data["aliases"]or ievent.channel not in cfg.data["aliases"][dest]:
        ievent.reply("%s is not an alias for %s" % (ievent.channel, dest))
        return

    cfg.data["aliases"][dest].remove(ievent.channel)
    ievent.reply("%s will no longer receive irccat messages directed at %s" % (ievent.channel, dest))
    cfg.save()
cmnds.add("irccat_del_alias", handle_irccat_del_alias, ['OPER'])
examples.add("irccat_del_alias", "add an alias to the current channel from the specified one", "irccat_del_alias #firebreath")

def handle_irccat_enable(bot, event):
    cfg.data.enable = True ; cfg.save() ; event.done()
    init_threaded()
    
cmnds.add("irccat-enable", handle_irccat_enable, "OPER")
examples.add("irccat-enable", "enable irccat server", "irccat-enable")

def handle_irccat_disable(bot, event):
    cfg.data.enable = False ; cfg.save() ; event.done()
    shutdown()
    
cmnds.add("irccat-disable", handle_irccat_disable, "OPER")
examples.add("irccat-disable", "disable irccat server", "irccat-disable")
