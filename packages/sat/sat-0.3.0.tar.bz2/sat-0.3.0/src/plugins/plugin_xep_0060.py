#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SAT plugin for Publish-Subscribe (xep-0060)
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
from twisted.internet import protocol
from twisted.words.protocols.jabber import client, jid
from twisted.words.protocols.jabber import error as jab_error
import twisted.internet.error

from wokkel import disco, iwokkel, pubsub

from zope.interface import implements

PLUGIN_INFO = {
"name": "Publish-Subscribe",
"import_name": "XEP-0060",
"type": "XEP",
"protocols": ["XEP-0060"],
"dependencies": [],
"main": "XEP_0060",
"handler": "yes",
"description": _("""Implementation of PubSub Protocol""")
}

class XEP_0060():

    def __init__(self, host):
        info(_("PubSub plugin initialization"))
        self.host = host
        self.managedNodes=[]
        self.clients={}
        """host.bridge.addMethod("getItems", ".plugin", in_sign='ssa{ss}s', out_sign='as', method=self.getItems,
                              async = True,
                              doc = { 'summary':'retrieve items',
                                      'param_0':'service: pubsub service',
                                      'param_1':'node: node identifier',
                                      'param_2':'\n'.join(['options: can be:',
                                          '- max_items: see XEP-0060 #6.5.7',
                                          '- sub_id: subscription identifier, see XEP-0060 #7.2.2.2']),
                                      'param_3':'%(doc_profile)s',
                                      'return':'array of raw XML (content of the items)'
                                    })"""

    def getHandler(self, profile):
        self.clients[profile] = SatPubSubClient(self.host, self)
        return self.clients[profile]

    def addManagedNode(self, node_name, callback):
        """Add a handler for a namespace
        @param namespace: NS of the handler (will appear in disco info)
        @param callback: method to call when the handler is found
        @param profile: profile which manage this handler"""
        self.managedNodes.append((node_name, callback))

    def __getClientNProfile(self, profile_key, action='do pusbsub'):
        """Return a tuple of (client, profile)
        raise error when the profile doesn't exists
        @param profile_key: as usual :)
        @param action: text of action to show in case of error"""
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            err_mess = _('Trying to %(action)s with an unknown profile key [%(profile_key)s]') % {
                         'action':action,
                         'profile_key':profile_key}
            error(err_mess)
            raise Exception(err_mess)
        try:
            client = self.clients[profile]
        except KeyError:
            err_mess = _('INTERNAL ERROR: no handler for required profile')
            error(err_mess)
            raise Exception(err_mess)
        return profile, client

    def publish(self, service, nodeIdentifier, items=None, profile_key='@DEFAULT@'):
        profile,client = self.__getClientNProfile(profile_key, 'publish item')
        return client.publish(service, nodeIdentifier, items, client.parent.jid) 

    def getItems(self, service, node, max_items=None, sub_id=None, profile_key='@DEFAULT@'):
        profile,client = self.__getClientNProfile(profile_key, 'get items')
        return client.items(service, node, max_items, sub_id, client.parent.jid)

    def getOptions(self, service, nodeIdentifier, subscriber, subscriptionIdentifier=None, profile_key='@DEFAULT@'):
        profile,client = self.__getClientNProfile(profile_key, 'get options')
        return client.getOptions(service, nodeIdentifier, subscriber, subscriptionIdentifier)

    def setOptions(self, service, nodeIdentifier, subscriber, options, subscriptionIdentifier=None, profile_key='@DEFAULT@'):
        profile,client = self.__getClientNProfile(profile_key, 'set options')
        return client.setOptions(service, nodeIdentifier, subscriber, options, subscriptionIdentifier)
    
    def createNode(self, service, nodeIdentifier, options, profile_key='@DEFAULT@'):
        profile,client = self.__getClientNProfile(profile_key, 'create node')
        return client.createNode(service, nodeIdentifier, options)

    def deleteNode(self, service, nodeIdentifier, profile_key='@DEFAULT@'):
        profile,client = self.__getClientNProfile(profile_key, 'delete node')
        return client.deleteNode(service, nodeIdentifier)
    
    def subscribe(self, service, nodeIdentifier, sub_jid = None, options=None, profile_key='@DEFAULT@'):
        profile,client = self.__getClientNProfile(profile_key, 'subscribe node')
        return client.subscribe(service, nodeIdentifier, sub_jid or client.parent.jid.userhostJID(), options=options) 

        
class SatPubSubClient(pubsub.PubSubClient):
    implements(disco.IDisco)

    def __init__(self, host, parent_plugin):
        self.host=host
        self.parent_plugin = parent_plugin
        pubsub.PubSubClient.__init__(self)

    def connectionInitialized(self):
        pubsub.PubSubClient.connectionInitialized(self)
    
    def itemsReceived(self, event):
        if not self.host.trigger.point("PubSubItemsReceived", event, self.parent.profile):
            return
        for node in self.parent_plugin.managedNodes:
            if event.nodeIdentifier == node[0]:
                return node[1](event, self.parent.profile)

    def deleteReceived(self, event):
        #TODO: manage delete event
        debug(_("Publish node deleted"))

    def purgeReceived(self, event):
        import pdb
        pdb.set_trace()

    def getDiscoInfo(self, requestor, target, nodeIdentifier=''):
        _disco_info = []
        self.host.trigger.point("PubSub Disco Info", _disco_info, self.parent.profile)
        return _disco_info
    
    def getDiscoItems(self, requestor, target, nodeIdentifier=''):
        return []

