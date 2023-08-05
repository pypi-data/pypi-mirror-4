# jsb/plugs/core/botevent.py
#
#

""" provide handling of host/tasks/botevent tasks. """

## jsb imports

from ggz.utils.exception import handle_exception
from ggz.lib.tasks import taskmanager
from ggz.lib.botbase import BotBase
from ggz.lib.eventbase import EventBase
from ggz.utils.lazydict import LazyDict
from ggz.lib.factory import BotFactory
from ggz.lib.callbacks import first_callbacks, callbacks, last_callbacks

## simplejson imports

from ggz.imports import getjson
json = getjson()

## basic imports

import logging

## boteventcb callback

def boteventcb(inputdict, request, response):
    #logging.warn(inputdict)
    #logging.warn(dir(request))
    #logging.warn(dir(response))
    body = request.body
    #logging.warn(body)
    payload = json.loads(body)
    try:
        botjson = payload['bot']
        logging.warn(botjson)
        cfg = LazyDict(json.loads(botjson))
        #logging.warn(str(cfg))
        bot = BotFactory().create(cfg.type, cfg)
        logging.warn("created bot: %s" % bot.tojson(full=True))
        eventjson = payload['event']
        #logging.warn(eventjson)
        event = EventBase()
        event.update(LazyDict(json.loads(eventjson)))
        logging.warn("created event: %s" % event.tojson(full=True))
        event.isremote = True
        event.notask = True
        bot.doevent(event)
    except Exception as ex: handle_exception()

taskmanager.add('botevent', boteventcb)

