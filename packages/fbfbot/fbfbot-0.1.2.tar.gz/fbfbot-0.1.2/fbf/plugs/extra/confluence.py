# fbf/plugs/socket/confluence.py
#
#

"""
confluence.py - fbfbot module for performing lookups on a confluence server
Copyright 2011, Richard Bateman

Special thanks to Sean B. Palmer for his phenny module; many of the ideas for
this were adapted from that plugin

http://inamidst.com/phenny/

BHJTW: adapted for FBFBOT on 15-09-2012

"""

## fbf imports

from fbf.lib.callbacks import callbacks
from fbf.lib.commands import cmnds
from fbf.lib.persist import PlugPersist
from fbf.lib.examples import examples
from fbf.plugs.extra.tinyurl import get_tinyurl

## basic imports

import logging
import xmlrpc.client
import re
import time

#import modules.activecollab

## defines

rpc_clients = {}
cfg = PlugPersist('confluence', {})

## fetRpcClient function

def getRpcClient(sInfo):
    if sInfo["name"] not in rpc_clients:
        base_url = "%s/rpc/xmlrpc" % sInfo["url"]
        server = xmlrpc.client.ServerProxy(base_url).confluence1

        username, password = sInfo["username"], sInfo["password"]
        auth = server.login(username, password)

        rpc_clients[sInfo["name"]] = (server, auth)

    return rpc_clients[sInfo["name"]]

## confluence-add_confluence_server command

def handle_add_confluence_server(bot, ievent):
    """ configure a new confluence server; syntax: add_confluence_server [server name] [url] [username] [password] """
    if len(ievent.args) != 4:
        ievent.reply("syntax: add_confluence_server [server name] [url] [username] [password]")
        return

    server = {
        "name": ievent.args[0],
        "url": ievent.args[1].strip("/"),
        "username": ievent.args[2],
        "password": ievent.args[3],
        "channels": {},
        "serverInfo": {},
    }

    if "servers" not in cfg.data:
        cfg.data["servers"] = {}
    cfg.data["servers"][server["name"]] = server
    cfg.save()

    ievent.reply("Added confluence server %s" % server["name"])
cmnds.add("add_confluence_server", handle_add_confluence_server, ["OPER"])
examples.add("add_confluence_server", "add a confluence server", "add_confluence_server FireBreath http://confluence.firebreath.org myuser mypassword")

def handle_del_confluence_server(bot, ievent):
    """ remove a confluence server; syntax: del_confluence_server """
    if len(ievent.args) != 1:
        ievent.reply("syntax: del_confluence_server [server name]")
        return

    serverName = ievent.args[0]
    if "servers" not in cfg.data:
        cfg.data["servers"] = {}
    if serverName in cfg.data["servers"]:
        del cfg.data["servers"][serverName]
        cfg.save()
        ievent.reply("Deleted confluence server %s" % serverName)
    else:
        ievent.reply("Unknown confluence server %s" % serverName)
cmnds.add("del_confluence_server", handle_del_confluence_server, ["OPER"])
examples.add("del_confluence_server", "del a confluence server", "del_confluence_server FireBreath http://confluence.firebreath.org myuser mypassword")

def handle_confluence_enable_server(bot, ievent):
    """ choose the confluence server for lookups in the current channel; syntax: handle_confluence_enable_server [server] """
    if len(ievent.args) != 1:
        ievent.reply("syntax: handle_confluence_enable_server [server]")
        return

    serverName = ievent.args[0]
    if not "servers" in cfg.data or not serverName in cfg.data["servers"]:
        ievent.reply("Unknown server %s" % serverName)
        return

    if not "channels" in cfg.data:
        cfg.data["channels"] = {}

    cfg.data["channels"][ievent.channel] = serverName
    cfg.save()
    ievent.reply("enabled confluence searches from this channel for server %s" % serverName)
cmnds.add("confluence_enable_server", handle_confluence_enable_server, ["OPER"])
examples.add("confluence_enable_server", "enable searching confluence from the channel", "confluence_enable_server confluenceserver")

## confluence-disable command

def handle_confluence_disable(bot, ievent):
    """ disable lookups for confluence in the current channel; syntax: confluence_disable """
    if not "channels" in cfg.data or not ievent.channel in cfg.data["channels"]:
        ievent.reply("Confluence search was not enabled on this channel")
        return

    del cfg.data["channels"][ievent.channel]
    ievent.reply("disabled confluence searching from this channel")
cmnds.add("confluence_disable", handle_confluence_disable, ["OPER"])
examples.add("confluence_disable", "disable lookups for confluence in the current channel", "confluence_disable")

## wiki command

def handle_confluence_search(bot, ievent):

    if "channels" not in cfg.data or ievent.channel not in cfg.data["channels"]:
        ievent.reply("Confluence wiki search not enabled for this channel")
        return

    serverName = cfg.data["channels"][ievent.channel]
    server = cfg.data["servers"][serverName]

    if len(ievent.args) == 0:
        ievent.reply("The wiki is located at %s" % server["url"])
        return
    args = ievent.args
    if args[0][0] == "#":
        maxResults = int(args[0].strip("#"))
        args = args[1:]
    else:
        maxResults = 5

    query = " ".join(args)

    try:
        client, auth = getRpcClient(server)
        results = client.search(auth, query, maxResults)
    except Exception as ex: ievent.reply("an error occured: %s" % str(ex)) ; return

    ievent.reply("Displaying %s result(s) :" % min(maxResults, len(results)))
    for page in results[:maxResults]:
        tinyurl = get_tinyurl(page["url"])
        tinyurl = tinyurl[0] if tinyurl else page["url"]
        ievent.reply('"%s": %s' % (page["title"], tinyurl))

cmnds.add("wiki", handle_confluence_search, ["OPER", "USER", "GUEST"])
examples.add("wiki", "perform a lookup in the selected confluence instance", "wiki #5 some search text")
