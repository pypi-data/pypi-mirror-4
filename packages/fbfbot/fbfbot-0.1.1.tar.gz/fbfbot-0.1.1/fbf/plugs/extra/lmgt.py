
from fbf.lib.commands import cmnds
from fbf.plugs.extra.tinyurl import get_tinyurl
from urllib.parse import quote, unquote

def handle_lmgt(bot, ievent):
    """ google something for them; syntax: lmgt [search terms] """
    if len(ievent.args) < 1:
        ievent.reply("syntax: lmgt [search terms]")
        return

    a = "http://lmgtfy.com/?q=%s" % quote(" ".join(ievent.args))
    ievent.reply("Let me google that for you: %s" % get_tinyurl(a)[0])

cmnds.add("lmgt", handle_lmgt, ["OPER", "USER", "GUEST"])

