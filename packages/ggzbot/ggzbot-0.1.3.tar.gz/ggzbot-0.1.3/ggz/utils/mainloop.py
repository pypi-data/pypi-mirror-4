# jsb/utils/mainloop.py
#
#

""" main loop used in jsb binairies. """

## jsb imports

from ggz.utils.exception import handle_exception
from ggz.lib.eventhandler import mainhandler
from ggz.lib.exit import globalshutdown

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
