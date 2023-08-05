# fbf/plugs/core/misc.py
#
#

""" misc commands. """

## fbf imports

from fbf.utils.exception import handle_exception
from fbf.lib.commands import cmnds
from fbf.lib.examples import examples
from fbf.lib.persiststate import UserState

## basic imports

import time
import os
import threading
import _thread
import copy

## defines

cpy = copy.deepcopy

## test command

def handle_test(bot, ievent):
    """ no arguments - give test response. """
    ievent.reply("%s (%s) - %s - it works!" % (ievent.auth or ievent.userhost, ievent.nick, ievent.user.data.name))
    
cmnds.add('test', handle_test, ['USER', 'GUEST'])
examples.add('test', 'give test response',' test')

## source command

def handle_source(bot, ievent):
    """ no arguments - show where to fetch the bot source. """ 
    ievent.reply('see http://fbfbot.googlecode.com and http:///docs/fbfbot')

cmnds.add('source', handle_source, ['USER', 'GUEST'])
examples.add('source', 'show source url', 'source')
