# fbf/plugs/core/botevent.py
#
#

""" provide handling of host/tasks/botevent tasks. """

## fbf imports

from fbf.lib.tasks import taskmanager
from fbf.lib.botbase import BotBase
from fbf.lib.eventbase import EventBase
from fbf.utils.lazydict import LazyDict
from fbf.lib.factory import BotFactory
from fbf.lib.callbacks import first_callbacks, callbacks, last_callbacks

## simplejson imports

from fbf.imports import getjson
json = getjson()

## basic imports

import logging

## boteventcb callback

def boteventcb(inputdict, request, response):
    body = request.body
    payload = json.loads(body)
    botjson = payload['bot']
    logging.warn(botjson)
    cfg = LazyDict(json.loads(botjson))
    bot = BotFactory().create(cfg.type, cfg)
    logging.warn("created bot: %s" % bot.tojson(full=True))
    eventjson = payload['event']
    event = EventBase()
    event.update(LazyDict(json.loads(eventjson)))
    logging.warn("created event: %s" % event.tojson(full=True))
    event.isremote = True
    event.notask = True
    bot.doevent(event)

taskmanager.add('botevent', boteventcb)

