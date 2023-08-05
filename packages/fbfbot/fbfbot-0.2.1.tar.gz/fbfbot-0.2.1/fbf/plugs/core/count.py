# fbf/plugs/core/count.py
#
#

""" count number of items in result queue. """

## fbf imports

from fbf.lib.commands import cmnds
from fbf.utils.generic import waitforqueue
from fbf.lib.examples import examples

## basic imports

import time

## count command

def handle_count(bot, ievent):
    """ no arguments - show nr of elements in result list .. use this command in a pipeline. """
    #if ievent.prev: ievent.prev.wait()
    a = ievent.inqueue
    size = len(a)
    ievent.reply(str(size))

cmnds.add('count', handle_count, ['OPER', 'USER', 'GUEST'])
examples.add('count', 'count nr of items', 'list ! count')
