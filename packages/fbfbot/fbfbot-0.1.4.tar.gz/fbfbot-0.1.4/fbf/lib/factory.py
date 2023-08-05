# fbf/lib/factory.py
#
#

""" Factory to produce instances of classes. """

## fbf imports

from fbf.utils.exception import handle_exception
from fbf.lib.errors import NoSuchBotType, NoUserProvided

## basic imports

import logging

## Factory base class

class Factory(object):
     pass

## BotFactory class

class BotFactory(Factory):

    def create(self, type=None, cfg={}):
        try: type = cfg['type'] or type or None
        except KeyError: pass
        try:
            if type == 'irc':
                from fbf.drivers.irc.bot import IRCBot
                bot = IRCBot(cfg)
            elif type == 'console':
                from fbf.drivers.console.bot import ConsoleBot
                bot = ConsoleBot(cfg)
            elif type == 'base':
                from fbf.lib.botbase import BotBase
                bot = BotBase(cfg)
            elif type == 'tornado':
                from fbf.drivers.tornado.bot import TornadoBot
                bot = TornadoBot(cfg)
            elif type == 'sleek' or "xmpp" in type:
                from fbf.drivers.sleek.bot import SleekBot
                bot = SleekBot(cfg)
            else: raise NoSuchBotType('%s bot .. unproper type %s' % (type, cfg.dump()))
            return bot
        except NoUserProvided as ex: logging.info("%s - %s" % (cfg.name, str(ex)))
        except AssertionError as ex: logging.warn("%s - assertion error: %s" % (cfg.name, str(ex)))
        except Exception as ex: handle_exception()

bot_factory = BotFactory()
