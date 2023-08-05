# jsb/plugs/core/welcome.py
#
#

""" send welcome message. """

## jsb imports

from ggz.lib.commands import cmnds
from ggz.lib.examples import examples

## welcome command

def handle_welcome(bot, event):
    """ no arguments - display welcome message. """
    event.reply("Welcome to GGZBOT - you can give this bot commands. try !help .. or !todo or !shop or !feedback .. ;]")

cmnds.add('welcome', handle_welcome, ['OPER', 'USER', 'GUEST'])
examples.add('welcome', 'send welcome msg', 'welcome')
