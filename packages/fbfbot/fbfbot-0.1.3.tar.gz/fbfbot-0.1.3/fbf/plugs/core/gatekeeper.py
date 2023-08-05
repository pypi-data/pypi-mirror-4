# fbf/plugs/core/gatekeeper.py
#
#

""" gatekeeper commands. """

## fbf imports

from fbf.lib.commands import cmnds
from fbf.lib.examples import examples

## gatekeeper-allow command

def handle_gatekeeperallow(bot, event):
    """ arguments: <userhost> - allow user on bot. """
    if not event.rest: event.missing("<userhost>") ; return
    bot.gatekeeper.allow(event.rest)
    event.done()

cmnds.add('gatekeeper-allow', handle_gatekeeperallow, 'OPER')
examples.add('gatekeeper-allow', 'add JID of remote bot that we allow to receice events from', 'gatekeeper-allow fbfbot@fbfprevenite.nl')

## gatekeeper-deny command

def handle_gatekeeperdeny(bot, event):
    """ arguments: userhost - deny user on bot. """
    if not event.rest: event.missing("<userhost>") ; return
    bot.gatekeeper.deny(event.rest)
    event.done()

cmnds.add('gatekeeper-deny', handle_gatekeeperdeny, 'OPER')
examples.add('gatekeeper-deny', 'remove JID of remote bot', 'gatekeeper-deny evilfscker@pissof.com')
