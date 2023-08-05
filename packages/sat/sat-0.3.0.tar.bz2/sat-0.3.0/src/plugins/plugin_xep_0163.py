#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SAT plugin for Personal Eventing Protocol (xep-0163)
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
from twisted.words.xish import domish

from wokkel import disco,pubsub
from wokkel.formats import Mood

NS_USER_MOOD = 'http://jabber.org/protocol/mood'

PLUGIN_INFO = {
"name": "Personal Eventing Protocol Plugin",
"import_name": "XEP-0163",
"type": "XEP",
"protocols": ["XEP-0163", "XEP-0107"],
"dependencies": ["XEP-0060"],
"main": "XEP_0163",
"handler": "no",
"description": _("""Implementation of Personal Eventing Protocol""")
}

class XEP_0163():

    def __init__(self, host):
        info(_("PEP plugin initialization"))
        self.host = host
        self.pep_events=set()
        self.pep_out_cb={}
        host.trigger.add("PubSub Disco Info", self.disoInfoTrigger)
        host.bridge.addSignal("personalEvent", ".plugin", signature='ssa{ss}s') #args: from (jid), type(MOOD, TUNE, etc), data, profile
        host.bridge.addMethod("sendPersonalEvent", ".plugin", in_sign='sa{ss}s', out_sign='i', method=self.sendPersonalEvent) #args: type(MOOD, TUNE, etc), data, profile_key; return 0 or error_code
        self.addPEPEvent("MOOD", NS_USER_MOOD, self.userMoodCB, self.sendMood)

    def disoInfoTrigger(self, disco_info, profile):
        """Add info from managed PEP
        @param disco_info: list of disco feature as returned by PubSub,
            will be filled with PEP features
        @param profile: profile we are handling"""
        disco_info.extend(map(disco.DiscoFeature, self.pep_events))
        return True

    def addPEPEvent(self, event_type, name, in_callback, out_callback = None, notify = True):
        """Add a Personal Eventing Protocol event manager
        @param event_type: type of the event (always uppercase), can be MOOD, TUNE, etc
        @param name: namespace of the node (e.g. http://jabber.org/protocol/mood for User Mood)
        @param in_callback: method to call when this event occur
        @param out_callback: method to call when we want to publish this event
        @param notify: add autosubscribe (+notify) if True"""
        if out_callback:
            self.pep_out_cb[event_type] = out_callback
        self.pep_events.add(name)
        if notify:
            self.pep_events.add(name+"+notify")
        self.host.plugins["XEP-0060"].addManagedNode(name, in_callback)

    def sendPEPEvent(self, namespace, data, profile):
        """Publish the event data
        @param namespace: node namespace
        @param data: domish.Element to use as payload
        @param profile: profile which send the data"""

        item = pubsub.Item(payload=data)
        self.host.plugins["XEP-0060"].publish(None, namespace, [item], profile_key = profile)

    def sendPersonalEvent(self, event_type, data, profile_key='@DEFAULT@'):
        """Send personal event after checking the data is alright
        @param event_type: type of event (eg: MOOD, TUNE), must be in self.pep_out_cb.keys()
        @param data: dict of {string:string} of event_type dependant data
        @param profile_key: profile who send the event
        @return: 0 if success, error code else"""
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            error(_('Trying to send personal event with an unknown profile key [%s]') % profile_key)
            return 1
        if not event_type in self.pep_out_cb.keys():
            error (_('Trying to send personal event for an unknown type'))
            return 2
        return self.pep_out_cb[event_type](data, profile)

    def userMoodCB(self, itemsEvent, profile):
        if not itemsEvent.items:
            debug(_("No item found"))
            return
        try:
            mood_elem = filter(lambda x:x.name == "mood", itemsEvent.items[0].children)[0]
        except KeyError:
            error(_("Can't find mood element in mood event"))
            return
        _mood = Mood.fromXml(mood_elem)
        if not _mood:
            debug(_("No mood found"))
            return
        self.host.bridge.personalEvent(itemsEvent.sender.full(), "MOOD", {"mood":_mood.value or "", "text":_mood.text or ""}, profile)

    def sendMood(self, data, profile):
        """Send XEP-0107's User Mood
        @param data: must include mood and text
        @param profile: profile which send the mood"""
        try:
            value = data['mood'].lower()
            text = data['text'] if data.has_key('text') else ''
        except KeyError:
            error(_("Mood data must contain at least 'mood' key"))
            return 3
        _mood = UserMood(value, text)
        self.sendPEPEvent(NS_USER_MOOD, _mood, profile)
        return 0

class UserMood(Mood, domish.Element):
    """Improved wokkel Mood which is also a domish.Element"""

    def __init__(self, value, text=None):
        Mood.__init__(self, value, text)
        domish.Element.__init__(self, (NS_USER_MOOD, 'mood'))
        self.addElement(value)
        if text:
            self.addElement('text', content=text)

