#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SAT plugin for managing xep-0115
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

from logging import debug, info, error, warning
from twisted.words.xish import domish
from twisted.words.protocols.jabber import client, jid, xmlstream
from twisted.words.protocols.jabber import error as jab_error
from twisted.words.protocols.jabber.xmlstream import IQ
from sat.memory.persistent import PersistentBinaryDict
import os.path
import types

from zope.interface import implements

from wokkel import disco, iwokkel

from hashlib import sha1
from base64 import b64encode

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

PRESENCE = '/presence'
NS_ENTITY_CAPABILITY = 'http://jabber.org/protocol/caps'
CAPABILITY_UPDATE = PRESENCE + '/c[@xmlns="' +  NS_ENTITY_CAPABILITY + '"]'

PLUGIN_INFO = {
"name": "XEP 0115 Plugin",
"import_name": "XEP-0115",
"type": "XEP",
"protocols": ["XEP-0115"],
"dependencies": [],
"main": "XEP_0115",
"handler": "yes",
"description": _("""Implementation of entity capabilities""")
}

class HashGenerationError(Exception):
    pass

class ByteIdentity(object):
    """This class manage identity as bytes (needed for i;octet sort),
    it is used for the hash generation"""

    def __init__(self, identity, lang=None):
        assert isinstance(identity, disco.DiscoIdentity)
        self.category = identity.category.encode('utf-8')
        self.idType = identity.type.encode('utf-8')
        self.name = identity.name.encode('utf-8') if identity.name else ''
        self.lang = lang.encode('utf-8') if lang else ''

    def __str__(self):
        return "%s/%s/%s/%s" % (self.category, self.idType, self.lang, self.name)
           

class XEP_0115():
    cap_hash = None #capabilities hash is class variable as it is common to all profiles
    #TODO: this code is really dirty, need to clean it and try to move it to Wokkel

    def __init__(self, host):
        info(_("Plugin XEP_0115 initialization"))
        self.host = host
        host.trigger.add("Disco Handled", self.checkHash)
        self.hash_cache = PersistentBinaryDict(NS_ENTITY_CAPABILITY) #key = hash or jid, value = features
        self.hash_cache.load()
        self.jid_hash = {} #jid to hash mapping, map to a discoInfo features if the hash method is unknown 

    def checkHash(self, profile):
        if not XEP_0115.cap_hash:
            XEP_0115.cap_hash = self.generateHash(profile)
        else:
            self.presenceHack(profile)
        return True
        
    def getHandler(self, profile):
        return XEP_0115_handler(self, profile)

    def presenceHack(self, profile):
        """modify SatPresenceProtocol to add capabilities data"""
        client=self.host.getClient(profile)
        presenceInst = client.presence
        c_elt = domish.Element((NS_ENTITY_CAPABILITY,'c'))
        c_elt['hash']='sha-1'
        c_elt['node']='http://wiki.goffi.org/wiki/Salut_%C3%A0_Toi'
        c_elt['ver']=XEP_0115.cap_hash
        presenceInst._c_elt = c_elt
        if "_legacy_send" in dir(presenceInst):
            debug('capabilities already added to presence instance')
            return
        def hacked_send(self, obj):
            obj.addChild(self._c_elt)
            self._legacy_send(obj)
        new_send = types.MethodType(hacked_send, presenceInst, presenceInst.__class__)
        presenceInst._legacy_send = presenceInst.send
        presenceInst.send = new_send


    def generateHash(self, profile_key="@DEFAULT@"):
        """This method generate a sha1 hash as explained in xep-0115 #5.1
        it then store it in XEP_0115.cap_hash"""
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            error ('Requesting hash for an inexistant profile')
            raise HashGenerationError

        client = self.host.getClient(profile_key)
        if not client:
            error ('Requesting hash for an inexistant client')
            raise HashGenerationError
        
        def generateHash_2(services, profile):
            _s=[]
            byte_identities = [ByteIdentity(identity) for identity in filter(lambda x:isinstance(x,disco.DiscoIdentity),services)] #FIXME: lang must be managed here
            byte_identities.sort(key=lambda i:i.lang)
            byte_identities.sort(key=lambda i:i.idType)
            byte_identities.sort(key=lambda i:i.category)
            for identity in byte_identities:
                _s.append(str(identity))
                _s.append('<')
            byte_features = [feature.encode('utf-8') for feature in filter(lambda x:isinstance(x,disco.DiscoFeature),services)]
            byte_features.sort() #XXX: the default sort has the same behaviour as the requested RFC 4790 i;octet sort
            for feature in byte_features:
                _s.append(feature)
                _s.append('<')
            #TODO: manage XEP-0128 data form here
            XEP_0115.cap_hash = b64encode(sha1(''.join(_s)).digest())
            debug(_('Capability hash generated: [%s]') % XEP_0115.cap_hash)
            self.presenceHack(profile)
            
        services = client.discoHandler.info(client.jid, client.jid, '').addCallback(generateHash_2, profile)
   
class XEP_0115_handler(XMPPHandler):
    implements(iwokkel.IDisco)
   
    def __init__(self, plugin_parent, profile):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host
        self.profile = profile

    def connectionInitialized(self):
        self.xmlstream.addObserver(CAPABILITY_UPDATE, self.update)
    
    def getDiscoInfo(self, requestor, target, nodeIdentifier=''):
        return [disco.DiscoFeature(NS_ENTITY_CAPABILITY)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=''):
        return []

    def _updateCache(self, discoResult, from_jid, key):
        """Actually update the cache
        @param discoResult: result of the requestInfo"""
        if key:
            self.plugin_parent.jid_hash[from_jid] = key
            self.plugin_parent.hash_cache[key] = discoResult.features
        else:
            #No key, that means unknown hash method
            self.plugin_parent.jid_hash[from_jid] = discoResult.features


    def update(self, presence):
        """
        Manage the capabilities of the entity
        Check if we know the version of this capatilities
        and get the capibilities if necessary
        """
        from_jid = jid.JID(presence['from'])
        c_elem = filter (lambda x:x.name == "c", presence.elements())[0] #We only want the "c" element
        try:
            ver=c_elem['ver']
            hash=c_elem['hash']
            node=c_elem['node']
        except KeyError:
            warning('Received invalid capabilities tag')
            return
        if not from_jid in self.plugin_parent.jid_hash:
            if ver in self.plugin_parent.hash_cache:
                #we know that hash, we just link it with the jid
                self.plugin_parent.jid_hash[from_jid] = ver
            else:
                if hash!='sha-1':
                    #unknown hash method
                    warning('Unknown hash for entity capabilities: [%s]' % hash)
                self.parent.disco.requestInfo(from_jid).addCallback(self._updateCache, from_jid, ver if hash=='sha-1' else None )
        #TODO: me must manage the full algorithm described at XEP-0115 #5.4 part 3

