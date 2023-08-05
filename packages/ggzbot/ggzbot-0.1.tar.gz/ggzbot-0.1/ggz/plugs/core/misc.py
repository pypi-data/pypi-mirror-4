# jsb/plugs/core/misc.py
#
#

""" misc commands. """

## jsb imports

from ggz.utils.exception import handle_exception
from ggz.lib.commands import cmnds
from ggz.lib.examples import examples
from ggz.lib.persiststate import UserState

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
    ievent.reply('see http://jsonbot.googlecode.com')

cmnds.add('source', handle_source, ['USER', 'GUEST'])
examples.add('source', 'show source url', 'source')
