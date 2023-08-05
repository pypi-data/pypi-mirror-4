# jsb/plugs/core/uniq.py
#
#

""" used in a pipeline .. unique elements. """

__author__ = "Wijnand 'tehmaze' Modderman - http://tehmaze.com"
__license__ = 'BSD'

## jsb imports

from ggz.lib.examples import examples
from ggz.lib.commands import cmnds
from ggz.utils.generic import waitforqueue

## basic imports

import time

## uniq command

def handle_uniq(bot, ievent):
    """ no arguments - uniq the result list, use this command in a pipeline. """
    if not ievent.inqueue: time.sleep(0.5)
    result = list(ievent.inqueue)
    if not result: ievent.reply('no result')
    else: ievent.reply("result: ", result)

cmnds.add('uniq', handle_uniq, ['OPER', 'USER', 'GUEST'])
examples.add('uniq', 'sort out multiple elements', 'list ! uniq')
