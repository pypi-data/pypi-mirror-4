#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
helper class for making a SAT frontend
Copyright (C) 2009, 2010, 2011, 2012, 2013  Jérôme Poisson (goffi@goffi.org)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""




class QuickGatewaysManager():

    
    def __init__(self, host, gateways, title=_("Gateways manager"), server=None):
        self.WARNING_MSG = _(u"""Be careful ! Gateways allow you to use an external IM (legacy IM), so you can see your contact as jabber contacts.
But when you do this, all your messages go throught the external legacy IM server, it is a huge privacy issue (i.e.: all your messages throught the gateway can be monitored, recorded, analyzed by the external server, most of time a private company).""")
        self.host = host

    def getGatewayDesc(self, gat_type):
        """Return a human readable description of gateway type
        @param gat_type: type of gateway, as given by SàT"""
        desc = _('Unknown IM')

        if gat_type == 'irc':
            desc = "Internet Relay Chat"
        elif gat_type == 'xmpp':
            desc = "XMPP"
        elif gat_type == 'qq':
            desc = "Tencent QQ"
        elif gat_type == 'simple':
            desc = "SIP/SIMPLE"
        elif gat_type == 'icq':
            desc = "ICQ"
        elif gat_type == 'yahoo':
            desc = "Yahoo! Messenger"
        elif gat_type == 'gadu-gadu':
            desc = "Gadu-Gadu"
        elif gat_type == 'aim':
            desc = "AOL Instant Messenger"
        elif gat_type == 'msn':
            desc = 'Windows Live Messenger'

        return desc
