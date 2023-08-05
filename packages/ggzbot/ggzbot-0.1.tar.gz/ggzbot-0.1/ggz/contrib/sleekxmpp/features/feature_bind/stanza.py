"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2011  Nathanael C. Fritz
    This file is part of SleekXMPP.

    See the file LICENSE for copying permission.
"""

from sleekxmpp.stanza import Iq, StreamFeatures
from sleekxmpp.xmlstream import ElementBase, ET, register_stanza_plugin


class Bind(ElementBase):

    """
    """

    name = 'bind'
    namespace = 'urn:ietf:params:xml:ns:xmpp-bind'
    interfaces = set(('resource', 'jid'))
    sub_interfaces = interfaces
    plugin_attrib = 'bind'
