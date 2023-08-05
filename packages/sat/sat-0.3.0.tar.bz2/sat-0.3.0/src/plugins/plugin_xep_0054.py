#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SAT plugin for managing xep-0054
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
from twisted.internet import threads
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber.xmlstream import IQ
from twisted.words.xish import domish
import os.path

from zope.interface import implements

from wokkel import disco, iwokkel

from base64 import b64decode,b64encode
from hashlib import sha1
from sat.core import exceptions
from sat.memory.persistent import PersistentDict
import Image
from cStringIO import StringIO

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

AVATAR_PATH = "avatars"

IQ_GET = '/iq[@type="get"]'
NS_VCARD = 'vcard-temp'
VCARD_REQUEST = IQ_GET + '/vCard[@xmlns="' + NS_VCARD + '"]'  #TODO: manage requests

PRESENCE = '/presence'
NS_VCARD_UPDATE = 'vcard-temp:x:update'
VCARD_UPDATE = PRESENCE + '/x[@xmlns="' +  NS_VCARD_UPDATE + '"]'

PLUGIN_INFO = {
"name": "XEP 0054 Plugin",
"import_name": "XEP-0054",
"type": "XEP",
"protocols": ["XEP-0054", "XEP-0153"],
"dependencies": [],
"main": "XEP_0054",
"handler": "yes",
"description": _("""Implementation of vcard-temp""")
}

class XEP_0054():
    #TODO: - check that nickname is ok
    #      - refactor the code/better use of Wokkel
    #      - get missing values

    def __init__(self, host):
        info(_("Plugin XEP_0054 initialization"))
        self.host = host
        self.avatar_path = os.path.join(self.host.memory.getConfig('', 'local_dir'), AVATAR_PATH)
        if not os.path.exists(self.avatar_path):
            os.makedirs(self.avatar_path)
        self.avatars_cache = PersistentDict(NS_VCARD)
        self.avatars_cache.load() #FIXME: resulting deferred must be correctly managed
        host.bridge.addMethod("getCard", ".plugin", in_sign='ss', out_sign='s', method=self.getCard)
        host.bridge.addMethod("getAvatarFile", ".plugin", in_sign='s', out_sign='s', method=self.getAvatarFile)
        host.bridge.addMethod("setAvatar", ".plugin", in_sign='ss', out_sign='', method=self.setAvatar, async = True)
        host.trigger.add("presence_available", self.presenceTrigger)

    def getHandler(self, profile):
        return XEP_0054_handler(self)

    def presenceTrigger(self, presence_elt, client):
        if client.jid.userhost() in self.avatars_cache:
            x_elt = domish.Element((NS_VCARD_UPDATE, 'x'))
            x_elt.addElement('photo', content=self.avatars_cache[client.jid.userhost()])
            presence_elt.addChild(x_elt)
       
        return True
  
    def _fillCachedValues(self, result, client):
        #FIXME: this is really suboptimal, need to be reworked
        #       the current naive approach keeps a map between all jids of all profiles
        #       in persistent cache, and check if cached jid are in roster, then put avatar
        #       hashs in memory.
        for _jid in client.roster.getBareJids() + [client.jid.userhost()]:
            if _jid in self.avatars_cache:
                self.host.memory.updateEntityData(jid.JID(_jid), "avatar", self.avatars_cache[_jid], client.profile)
        
    def profileConnected(self, profile):
        client = self.host.getClient(profile)
        client.roster.got_roster.addCallback(self._fillCachedValues, client)
    
    def update_cache(self, jid, name, value, profile):
        """update cache value
        - save value in memory in case of change
        @param jid: jid of the owner of the vcard
        @param name: name of the item which changed
        @param value: new value of the item
        @param profile: profile which received the update
        """
        try:
            cached = self.host.memory.getEntityData(jid, [name], profile)
        except exceptions.UnknownEntityError:
            cached = {}
        if not name in cached or cached[name] != value:
            self.host.memory.updateEntityData(jid, name, value, profile)
            if name == "avatar":
                self.avatars_cache[jid.userhost()] = value
            
    def get_cache(self, jid, name, profile):
        """return cached value for jid
        @param jid: target contact
        @param name: name of the value ('nick' or 'avatar')
        @param profile: %(doc_profile)s
        @return: wanted value or None"""
        try:
            data = self.host.memory.getEntityData(jid, [name], profile)
        except exceptions.UnknownEntityError:
            return None
        return data.get(name)

    def save_photo(self, photo_xml):
        """Parse a <PHOTO> elem and save the picture"""
        for elem in photo_xml.elements():
            if elem.name == 'TYPE':
                info(_('Photo of type [%s] found') % str(elem))
            if elem.name == 'BINVAL':
                debug(_('Decoding binary'))
                decoded = b64decode(str(elem))
                image_hash = sha1(decoded).hexdigest()
                filename = self.avatar_path+'/'+image_hash
                if not os.path.exists(filename):
                    with open(filename,'wb') as file:
                        file.write(decoded)
                    debug(_("file saved to %s") % image_hash)
                else:
                    debug(_("file [%s] already in cache") % image_hash)
                return image_hash

    @inlineCallbacks
    def vCard2Dict(self, vcard, target, profile):
        """Convert a VCard to a dict, and save binaries"""
        debug (_("parsing vcard"))
        dictionary = {}
        
        for elem in vcard.elements():
            if elem.name == 'FN':
                dictionary['fullname'] = unicode(elem)
            elif elem.name == 'NICKNAME':
                dictionary['nick'] = unicode(elem)
                self.update_cache(target, 'nick', dictionary['nick'], profile)
            elif elem.name == 'URL':
                dictionary['website'] = unicode(elem)
            elif elem.name == 'EMAIL':
                dictionary['email'] = unicode(elem)
            elif elem.name == 'BDAY':
                dictionary['birthday'] = unicode(elem) 
            elif elem.name == 'PHOTO':
                dictionary["avatar"] = yield threads.deferToThread(self.save_photo, elem)
                if not dictionary["avatar"]:  #can happen in case of e.g. empty photo elem
                    del dictionary['avatar']
                else:
                    self.update_cache(target, 'avatar', dictionary['avatar'], profile)
            else:
                info (_('FIXME: [%s] VCard tag is not managed yet') % elem.name)

        returnValue(dictionary)

    def vcard_ok(self, answer, profile):
        """Called after the first get IQ"""
        debug (_("VCard found"))

        if answer.firstChildElement().name == "vCard":
            _jid, steam = self.host.getJidNStream(profile)
            try:
                from_jid = jid.JID(answer["from"])
            except KeyError:
                from_jid = _jid.userhostJID()
            d = self.vCard2Dict(answer.firstChildElement(), from_jid, profile)
            d.addCallback(lambda data: self.host.bridge.actionResult("RESULT", answer['id'], data, profile))
        else:
            error (_("FIXME: vCard not found as first child element"))
            self.host.bridge.actionResult("SUPPRESS", answer['id'], {}, profile) #FIXME: maybe an error message would be better

    def vcard_err(self, failure, profile):
        """Called when something is wrong with registration"""
        error (_("Can't find VCard of %s") % failure.value.stanza['from'])
        self.host.bridge.actionResult("SUPPRESS", failure.value.stanza['id'], {}, profile) #FIXME: maybe an error message would be better
  
    def getCard(self, target_s, profile_key='@DEFAULT@'):
        """Ask server for VCard
        @param target_s: jid from which we want the VCard
        @result: id to retrieve the profile"""
        current_jid, xmlstream = self.host.getJidNStream(profile_key)
        if not xmlstream:
            error (_('Asking vcard for a non-existant or not connected profile'))
            return ""
        profile = self.host.memory.getProfileName(profile_key)
        to_jid = jid.JID(target_s)
        debug(_("Asking for %s's VCard") % to_jid.userhost())
        reg_request=IQ(xmlstream,'get')
        reg_request["from"]=current_jid.full()
        reg_request["to"] = to_jid.userhost()
        reg_request.addElement('vCard', NS_VCARD)
        reg_request.send(to_jid.userhost()).addCallbacks(self.vcard_ok, self.vcard_err, callbackArgs=[profile], errbackArgs=[profile])
        return reg_request["id"] 

    def getAvatarFile(self, avatar_hash):
        """Give the full path of avatar from hash
        @param hash: SHA1 hash
        @return full_path
        """
        filename = self.avatar_path+'/'+avatar_hash
        if not os.path.exists(filename):
            error (_("Asking for an uncached avatar [%s]") % avatar_hash)
            return ""
        return filename

    def _buildSetAvatar(self, vcard_set, filepath):
        try:
            img = Image.open(filepath)
        except IOError:
            raise exceptions.DataError("Can't open image")

        if img.size != (64, 64):
            img = img.resize((64, 64))
        img_buf = StringIO()
        img.save(img_buf, 'PNG')

        vcard_elt = vcard_set.addElement('vCard', NS_VCARD)
        photo_elt = vcard_elt.addElement('PHOTO')
        photo_elt.addElement('TYPE', content='image/png')
        photo_elt.addElement('BINVAL', content=b64encode(img_buf.getvalue()))
        img_hash = sha1(img_buf.getvalue()).hexdigest()
        return (vcard_set, img_hash)

    def setAvatar(self, filepath, profile_key='@DEFAULT@'):
        """Set avatar of the profile
        @param filepath: path of the image of the avatar"""
        #TODO: This is a temporary way of setting avatar, as other VCard informations are not managed.
        #      A proper full VCard management should be done (and more generaly a public/private profile)
        client = self.host.getClient(profile_key)
        if not client:
            raise exceptions.NotConnectedProfileError(_('Trying to set avatar for a non-existant or not connected profile'))
        
        vcard_set = IQ(client.xmlstream,'set')
        d = threads.deferToThread(self._buildSetAvatar, vcard_set, filepath)
        
        def elementBuilt(result):
            """Called once the image is at the right size/format, and the vcard set element is build"""
            set_avatar_elt, img_hash = result
            self.avatars_cache[client.jid.userhost()] = img_hash # we need to update the hash, so we can send a new presence
                                                                 # element with the right hash 
            return set_avatar_elt.send().addCallback(lambda ignore: client.presence.available())
        
        d.addCallback(elementBuilt)
        
        return d


class XEP_0054_handler(XMPPHandler):
    implements(iwokkel.IDisco)
   
    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host

    def connectionInitialized(self):
        self.xmlstream.addObserver(VCARD_UPDATE, self.update)
    
    def getDiscoInfo(self, requestor, target, nodeIdentifier=''):
        return [disco.DiscoFeature(NS_VCARD)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=''):
        return []
    
    def update(self, presence):
        """Request for VCard's nickname
        return the cached nickname if exists, else get VCard
        """
        from_jid = jid.JID(presence['from'])
        #FIXME: wokkel's data_form should be used here
        x_elem = filter (lambda x:x.name == "x", presence.elements())[0] #We only want the "x" element
        for elem in x_elem.elements():
            if elem.name == 'photo':
                _hash = str(elem)
                old_avatar = self.plugin_parent.get_cache(from_jid, 'avatar', self.parent.profile)
                if not old_avatar or old_avatar != _hash:
                    debug(_('New avatar found, requesting vcard'))
                    self.plugin_parent.getCard(from_jid.userhost(), self.parent.profile)
