# jsb/console/event.py
#
#

""" a console event. """

## jsb imports

from ggz.lib.eventbase import EventBase
from ggz.lib.channelbase import ChannelBase
from ggz.lib.errors import NoInput

## basic imports

import getpass
import logging
import re

## ConsoleEvent class

class ConsoleEvent(EventBase):

    def parse(self, bot, input, console, *args, **kwargs):
        """ overload this. """
        if not input: raise NoInput()
        self.bot = bot
        self.console = console
        self.nick = getpass.getuser()
        self.auth = self.nick + '@' + bot.cfg.uuid
        self.userhost = self.auth
        self.origin = self.userhost
        self.txt = input
        self.channel = self.userhost
        self.cbtype = self.cmnd = str("CONSOLE")
        self.showall = True
        self.prepare()
        return self
        