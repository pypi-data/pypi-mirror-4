#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SAT plugin for managing xep-0249
Copyright (C) 2009, 2010, 2011, 2012, 2013 Jérôme Poisson (goffi@goffi.org)

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

from logging import debug, info, warning, error
from twisted.words.xish import domish
from twisted.internet import protocol, defer
from twisted.words.protocols.jabber import client, jid, xmlstream

from zope.interface import implements

from wokkel import disco, iwokkel, data_form


try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

MESSAGE= '/message'
NS_DIRECT_MUC_INVITATION = 'jabber:x:conference'
DIRECT_MUC_INVITATION_REQUEST = MESSAGE + '/x[@xmlns="' + NS_DIRECT_MUC_INVITATION + '"]'

PLUGIN_INFO = {
"name": "XEP 0249 Plugin",
"import_name": "XEP-0249",
"type": "XEP",
"protocols": ["XEP-0249"],
"dependencies": ["XEP-0045"],
"main": "XEP_0249",
"handler": "yes",
"description": _("""Implementation of Direct MUC Invitations""")
}

class XEP_0249():

    def __init__(self, host):
        info(_("Plugin XEP_0249 initialization"))
        self.host = host
        host.bridge.addMethod("inviteMUC", ".plugin", in_sign='sssa{ss}s', out_sign='', method=self._invite)

    def getHandler(self, profile):
        return XEP_0249_handler(self)

    def invite(self, target, room, options={}, profile_key='@DEFAULT@'):
        """
        Invite a user to a room
        @param target: jid of the user to invite
        @param room: jid of the room where the user is invited
        @options: attribute with extra info (reason, password) as in #XEP-0249
        @profile_key: %(doc_profile_key)s
        """
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            error(_("Profile doesn't exists !"))
            return
        message = domish.Element((None,'message'))
        message["to"] = target.full()
        x_elt = message.addElement('x',NS_DIRECT_MUC_INVITATION)
        x_elt['jid'] = room.userhost()
        for opt in options:
            x_elt[opt] = options[opt]
        self.host.profiles[profile].xmlstream.send(message)

    def _invite(self, target, service, roomId, options = {}, profile_key='@DEFAULT@'):
        """
        Invite an user to a room
        @param target: jid of the user to invite
        @param service: jid of the MUC service
        @param roomId: name of the room
        @param profile_key: %(doc_profile_key)s
        """
        #TODO: check parameters validity
        self.invite(jid.JID(target), jid.JID("%s@%s" % (roomId, service)), options, profile_key)


    def onInvitation(self, message, profile):
        """
        called when an invitation is received
        @param message: message element
        @profile: %(doc_profile)s
        """
        info(_('Invitation received for room %(room)s [%(profile)s]') % {'room':'','profile':profile})
        try:
            room = jid.JID(message.firstChildElement()['jid'])
        except:
            error(_('Error while parsing invitation'))
            return
        _jid, xmlstream = self.host.getJidNStream(profile)
        #TODO: we always autojoin so far, we need to add a parameter to autojoin/ignore invitations or let user choose to follow it
        d = self.host.plugins["XEP-0045"].join(room, _jid.user, {}, profile)


class XEP_0249_handler(XMPPHandler):
    implements(iwokkel.IDisco)
    
    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host

    def connectionInitialized(self):
        self.xmlstream.addObserver(DIRECT_MUC_INVITATION_REQUEST, self.plugin_parent.onInvitation, profile = self.parent.profile)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=''):
        return [disco.DiscoFeature(NS_DIRECT_MUC_INVITATION)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=''):
        return []
