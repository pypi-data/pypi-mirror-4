#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SAT plugin for managing gateways (xep-0100)
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

from logging import debug, info, error
from twisted.words.protocols.jabber import client as jabber_client, jid
from twisted.words.protocols.jabber import error as jab_error
import twisted.internet.error

PLUGIN_INFO = {
"name": "Gateways Plugin",
"import_name": "XEP-0100",
"type": "XEP",
"protocols": ["XEP-0100"],
"dependencies": ["XEP-0077"],
"main": "XEP_0100",
"description": _("""Implementation of Gateways protocol""")
}

class XEP_0100():

    def __init__(self, host):
        info(_("Gateways plugin initialization"))
        self.host = host
        self.__gateways = {}  #dict used to construct the answer to findGateways. Key = target jid
        host.bridge.addMethod("findGateways", ".plugin", in_sign='ss', out_sign='s', method=self.findGateways)
        host.bridge.addMethod("gatewayRegister", ".plugin", in_sign='ssa(ss)s', out_sign='s', method=self.gatewayRegister)

    def __inc_handled_items(self, request_id, profile):
        self.__gateways[request_id]['__handled_items']+=1

        if self.__gateways[request_id]['__total_items'] == self.__gateways[request_id]['__handled_items']:
            debug (_("All items checked for id [%s]") % str(request_id))
            
            del self.__gateways[request_id]['__total_items']
            del self.__gateways[request_id]['__handled_items']
            self.host.actionResultExt(request_id,"DICT_DICT",self.__gateways[request_id], profile)

    def discoInfo(self, disco, entity, request_id, profile):
        """Find disco infos about entity, to check if it is a gateway"""

        for identity in disco.identities:
            if identity[0] == 'gateway':
                print (_("Found gateway (%(jid)s): %(identity)s") % {'jid':entity.full(), 'identity':disco.identities[identity]})
                self.__gateways[request_id][entity.full()] = {
                    'name':disco.identities[identity],
                    'type':identity[1]
                }

        self.__inc_handled_items(request_id, profile)
    
    def discoInfoErr(self, failure, entity, request_id, profile):
        """Something is going wrong with disco"""
        failure.trap(jab_error.StanzaError,twisted.internet.error.ConnectionLost)
        error(_("Error when discovering [%(jid)s]: %(error)s") % {'jid':entity.full(), 'error':failure.getErrorMessage()})
        self.__inc_handled_items(request_id, profile)
        
    
    def discoItems(self, disco, request_id, target, client):
        """Look for items with disco protocol, and ask infos for each one"""
        #FIXME: target is used as we can't find the original iq node (parent is None)
        #       an other way would avoid this useless parameter (is there a way with wokkel ?)
        if len(disco._items) == 0:
            debug (_("No gateway found"))
            self.host.actionResultExt(request_id,"DICT_DICT",{})
            return

        self.__gateways[request_id] = {'__total_items':len(disco._items), '__handled_items':0, '__private__':{'target':target.full()}}
        for item in disco._items:
            #TODO: need to set a timeout for theses requests
            debug (_("item found: %s"), item.name)
            client.disco.requestInfo(item.entity).addCallback(self.discoInfo, entity=item.entity, request_id=request_id, profile=client.profile).addErrback(self.discoInfoErr, entity=item.entity, request_id=request_id, profile=client.profile)

    def discoItemsErr(self, failure, request_id, target, client):
        """Something is going wrong with disco"""
        error(_("Error when discovering [%(target)s]: %(condition)s") % {'target':target.full(), 'condition':unicode(failure.value)})
        message_data={"reason": "connection error", "message":_(u"Error while trying to discover %(target)s gateways: %(error_mess)s") % {'target':target.full(), 'error_mess':unicode(failure.value)}}
        self.host.bridge.actionResult("ERROR", request_id, message_data)


    def registrationSuccessful(self, target, profile):
        """Called when in_band registration is ok, we must now follow the rest of procedure"""
        debug (_("Registration successful, doing the rest"))
        self.host.addContact(target, profile)
        self.host.setPresence(target, profile)
    
    def gatewayRegister(self, action, target, fields, profile_key='@DEFAULT@'):
        """Register gateway using in-band registration, then log-in to gateway"""
        profile = self.host.memory.getProfileName(profile_key)
        assert(profile) #FIXME: return an error here
        if action == 'SUBMIT':
            self.host.plugins["XEP-0077"].addTrigger(target, self.registrationSuccessful, profile)
        return self.host.plugins["XEP-0077"].in_band_submit(action, target, fields, profile)

    def findGateways(self, target, profile_key):
        """Find gateways in the target JID, using discovery protocol
        Return an id used for retrieving the list of gateways
        """
        profile = self.host.memory.getProfileName(profile_key)
        client = self.host.getClient(profile_key)
        assert(client)
        to_jid = jid.JID(target)
        debug (_("find gateways (target = %(target)s, profile = %(profile)s)") % {'target':to_jid.full(), 'profile':profile})
        request_id = self.host.get_next_id()
        client.disco.requestItems(to_jid).addCallback(self.discoItems, request_id=request_id, target = to_jid, client = client).addErrback(self.discoItemsErr, request_id=request_id, target = to_jid, client = client)
        return request_id
