#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SAT plugin for managing xep-0095
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
from twisted.words.xish import domish
from twisted.internet import protocol
from twisted.words.protocols.jabber import client, jid
from twisted.words.protocols.jabber import error as jab_error
import os.path
from twisted.internet import reactor
import uuid

from zope.interface import implements

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

from wokkel import disco, iwokkel

IQ_SET = '/iq[@type="set"]'
NS_SI = 'http://jabber.org/protocol/si'
SI_REQUEST = IQ_SET + '/si[@xmlns="' + NS_SI + '"]'
SI_PROFILE_HEADER = "http://jabber.org/protocol/si/profile/"

PLUGIN_INFO = {
"name": "XEP 0095 Plugin",
"import_name": "XEP-0095",
"type": "XEP",
"protocols": ["XEP-0095"],
"main": "XEP_0095",
"handler": "yes",
"description": _("""Implementation of Stream Initiation""")
}

class XEP_0095():

    def __init__(self, host):
        info(_("Plugin XEP_0095 initialization"))
        self.host = host
        self.si_profiles = {} #key: SI profile, value: callback
    
    def getHandler(self, profile):
        return XEP_0095_handler(self)  

    def registerSIProfile(self, si_profile, callback):
        """Add a callback for a SI Profile
        param si_profile: SI profile name (e.g. file-transfer)
        param callback: method to call when the profile name is asked"""
        self.si_profiles[si_profile] =  callback

    def streamInit(self, iq_el, profile):
        """This method is called on stream initiation (XEP-0095 #3.2)
        @param iq_el: IQ element
        @param profile: %(doc_profile)s"""
        info (_("XEP-0095 Stream initiation"))
        iq_el.handled=True
        si_el = iq_el.firstChildElement()
        si_id = si_el.getAttribute('id')
        si_mime_type = iq_el.getAttribute('mime-type', 'application/octet-stream')
        si_profile = si_el.getAttribute('profile')
        si_profile_key =  si_profile[len(SI_PROFILE_HEADER):] if si_profile.startswith(SI_PROFILE_HEADER) else si_profile
        if self.si_profiles.has_key(si_profile_key):
            #We know this SI profile, we call the callback
            self.si_profiles[si_profile_key](iq_el['id'], iq_el['from'], si_id, si_mime_type, si_el, profile)
        else:
            #We don't know this profile, we send an error
            self.sendBadProfileError(iq_el['id'], iq_el['from'], profile)

    def sendRejectedError(self, iq_id, to_jid, reason = 'Offer Declined', profile='@NONE@'):
        """Helper method to send when the stream is rejected
        @param iq_id: IQ id
        @param to_jid: recipient
        @param reason: human readable reason (string)
        @param profile: %(doc_profile)s"""
        self.sendError(iq_id, to_jid, 403, 'cancel', {'text':reason}, profile=profile)

    def sendBadProfileError(self, iq_id, to_jid, profile):
        """Helper method to send when we don't know the SI profile
        @param iq_id: IQ id
        @param to_jid: recipient
        @param profile: %(doc_profile)s"""
        self.sendError(iq_id, to_jid, 400, 'modify', profile=profile)

    def sendBadRequestError(self, iq_id, to_jid, profile):
        """Helper method to send when we don't know the SI profile
        @param iq_id: IQ id
        @param to_jid: recipient
        @param profile: %(doc_profile)s"""
        self.sendError(iq_id, to_jid, 400, 'cancel', profile=profile)
    
    def sendFailedError(self, iq_id, to_jid, profile):
        """Helper method to send when we transfer failed
        @param iq_id: IQ id
        @param to_jid: recipient
        @param profile: %(doc_profile)s"""
        self.sendError(iq_id, to_jid, 500, 'cancel', {'custom':'failed'}, profile=profile) #as there is no error code for failed transfer, we use 500 (undefined-condition)
    
    def sendError(self, iq_id, to_jid, err_code, err_type='cancel', data={}, profile='@NONE@'):
        """Send IQ error as a result
        @param iq_id: IQ id
        @param to_jid: recipient
        @param err_code: error err_code (see XEP-0095 #4.2)
        @param err_type: one of cancel, modify
        @param data: error specific data (dictionary)
        @param profile: %(doc_profile)s
        """
        _client = self.host.getClient(profile)
        assert(_client)
        result = domish.Element((None, 'iq'))
        result['type'] = 'result'
        result['id'] = iq_id
        result['to'] = to_jid 
        error_el = result.addElement('error')
        error_el['err_code'] =  str(err_code)
        error_el['type'] = err_type
        if err_code==400 and err_type=='cancel':
            error_el.addElement(('urn:ietf:params:xml:ns:xmpp-stanzas','bad-request'))
            error_el.addElement((NS_SI,'no-valid-streams'))
        elif err_code==400 and err_type=='modify':
            error_el.addElement(('urn:ietf:params:xml:ns:xmpp-stanzas','bad-request'))
            error_el.addElement((NS_SI,'bad-profile'))
        elif err_code==403 and err_type=='cancel':
            error_el.addElement(('urn:ietf:params:xml:ns:xmpp-stanzas','forbidden'))
            if data.has_key('text'):
                error_el.addElement(('urn:ietf:params:xml:ns:xmpp-stanzas','text'), content=data['text'])
        elif err_code==500 and err_type=='cancel':
            condition_el = error_el.addElement((NS_SI,'undefined-condition'))
            if data.has_key('custom') and data['custom']=='failed':
                condition_el.addContent('Stream failed')

        _client.xmlstream.send(result)

    def acceptStream(self, iq_id, to_jid, feature_elt, misc_elts=[], profile='@NONE@'):
        """Send the accept stream initiation answer
        @param iq_id: IQ id
        @param feature_elt: domish element 'feature' containing stream method to use
        @param misc_elts: list of domish element to add
        @param profile: %(doc_profile)s"""
        _client = self.host.getClient(profile)
        assert(_client)
        info (_("sending stream initiation accept answer"))
        result = domish.Element((None, 'iq'))
        result['type'] = 'result'
        result['id'] = iq_id
        result['to'] = to_jid 
        si = result.addElement('si', NS_SI)
        si.addChild(feature_elt)
        for elt in misc_elts:
            si.addChild(elt)
        _client.xmlstream.send(result)

    def proposeStream(self, to_jid, si_profile, feature_elt, misc_elts, mime_type='application/octet-stream', profile_key='@NONE@'):
        """Propose a stream initiation
        @param to_jid: recipient (JID)
        @param si_profile: Stream initiation profile (XEP-0095)
        @param feature_elt: feature domish element, according to XEP-0020
        @param misc_elts: list of domish element to add for this profile
        @param mime_type: stream mime type
        @param profile: %(doc_profile)s
        @return: session id, offer"""
        current_jid, xmlstream = self.host.getJidNStream(profile_key)
        if not xmlstream:
            error (_('Asking for an non-existant or not connected profile'))
            return ""
        
        offer = client.IQ(xmlstream,'set')
        sid = str(uuid.uuid4()) 
        debug (_("Stream Session ID: %s") % offer["id"])

        offer["from"] = current_jid.full()
        offer["to"] = to_jid.full()
        si=offer.addElement('si',NS_SI)
        si['id'] = sid
        si["mime-type"] = mime_type
        si["profile"] = si_profile
        for elt in misc_elts:
            si.addChild(elt)
        si.addChild(feature_elt)

        offer.send()
        return sid, offer

    
class XEP_0095_handler(XMPPHandler):
    implements(iwokkel.IDisco)
    
    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host

    def connectionInitialized(self):
        self.xmlstream.addObserver(SI_REQUEST, self.plugin_parent.streamInit, profile = self.parent.profile)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=''):
        return [disco.DiscoFeature(NS_SI)] + [disco.DiscoFeature("http://jabber.org/protocol/si/profile/%s" % profile_name) for profile_name in self.plugin_parent.si_profiles]

    def getDiscoItems(self, requestor, target, nodeIdentifier=''):
        return []

