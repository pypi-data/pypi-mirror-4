# fbf/utils/mainloop.py
#
#

""" main loop used in fbf binairies. """

## fbf imports

from fbf.utils.exception import handle_exception
from fbf.lib.eventhandler import mainhandler
from fbf.lib.exit import globalshutdown

## basic imports

import os
import time

## mainloop function

def mainloop():
    """ function to be used as mainloop. """
    while 1:
        try:
            time.sleep(1)
            mainhandler.handle_one()
        except KeyboardInterrupt: break
        except Exception as ex:
            handle_exception()
            break
            #globalshutdown()
            #os._exit(1)
    globalshutdown()
    #os._exit(0)
