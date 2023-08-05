# jsb/plugs/core/remotecallbacks.py
#
#

""" dispatch remote events. """

## jsb imports

from ggz.utils.lazydict import LazyDict
from ggz.utils.generic import fromenc
from ggz.utils.exception import handle_exception
from ggz.lib.callbacks import callbacks, remote_callbacks, first_callbacks
from ggz.lib.container import Container
from ggz.lib.eventbase import EventBase
from ggz.lib.errors import NoProperDigest
from ggz.lib.commands import cmnds
from ggz.lib.examples import examples

## basic imports

import logging
import copy
import hmac
import hashlib
import cgi
import xml

## defines

XMLunescape = xml.sax.saxutils.unescape

cpy = copy.deepcopy

## callback

def remotecb(bot, event):
    """ dispatch an event. """
    try: container = Container().load(event.txt)
    except TypeError:
        handle_exception()
        logging.warn("remotecallbacks - not a remote event - %s " % event.userhost)
        return
    logging.debug('doing REMOTE callback')
    try:
        digest = hmac.new(bytes(container.hashkey, "utf-8"), bytes(XMLunescape(container.payload), "utf-8"), hashlib.sha512).hexdigest()
        logging.debug("remotecallbacks - digest is %s" % digest)
    except TypeError:
        handle_exception()
        logging.error("remotecallbacks - can't load payload - %s" % container.payload)
        return
    if container.digest == digest: e = EventBase().load(XMLunescape(container.payload))
    else: raise NoProperDigest()
    e.txt = XMLunescape(e.txt)
    e.nodispatch = True
    e.forwarded = True
    e.dontbind = True
    bot.doevent(e)
    event.status = "done"  
    return

remote_callbacks.add("MESSAGE", remotecb)
