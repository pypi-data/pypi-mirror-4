#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SAT: a jabber client
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

from sat.test import helpers
from twisted.trial import unittest
from sat.core.sat_main import SAT
from sat.core import xmpp
from twisted.internet import defer
from twisted.words.protocols.jabber.jid import JID
from wokkel.generic import parseXml
from wokkel.xmppim import RosterItem



class SatXMPPClientTest(unittest.TestCase):

    def setUp(self):
        self.host = helpers.FakeSAT()
        self.client = xmpp.SatXMPPClient(self.host, "test_profile", JID("test@example.org"), "test") 
        
    def test_init(self):
        """Check that init values are correctly initialised"""
        self.assertEqual(self.client.profile, "test_profile")
        print self.client.host
        self.assertEqual(self.client.host_app, self.host)
        self.assertTrue(isinstance(self.client.client_initialized, defer.Deferred))

class SatMessageProtocolTest(unittest.TestCase):

    def setUp(self):
        self.host = helpers.FakeSAT()
        self.message = xmpp.SatMessageProtocol(self.host)
        self.message.parent = helpers.FakeParent()

    def test_onMessage(self):
        xml = """
        <message type="chat" from="sender@example.net/house" to="test@example.org/SàT" id="test_1">
        <body>test</body>
        </message>
        """
        stanza = parseXml(xml)
        self.host.bridge.expectCall("newMessage", "sender@example.net/house", "test", "chat", u"test@example.org/SàT", profile="test_profile")
        self.message.onMessage(stanza)
    
class SatRosterProtocolTest(unittest.TestCase):

    def setUp(self):
        self.host = helpers.FakeSAT()
        self.roster = xmpp.SatRosterProtocol(self.host)
        self.roster.parent = helpers.FakeParent()

    def test_onRosterSet(self):
        roster_item = RosterItem(helpers.TEST_JID)
        roster_item.name = u"Test Man"
        roster_item.subscriptionTo = True
        roster_item.subscriptionFrom = True
        roster_item.ask = False
        roster_item.groups = set([u"Test Group 1", u"Test Group 2", u"Test Group 3"])
        self.host.bridge.expectCall("newContact", helpers.TEST_JID_STR, {'to':'True', 'from': 'True', 'ask': 'False', 'name': u'Test Man'}, set([u"Test Group 1", u"Test Group 2", u"Test Group 3"]), "test_profile")
        self.roster.onRosterSet(roster_item)

class SatPresenceProtocolTest(unittest.TestCase):

    def setUp(self):
        self.host = helpers.FakeSAT()
        self.presence = xmpp.SatPresenceProtocol(self.host)
        self.presence.parent = helpers.FakeParent()

    def test_availableReceived(self):
        self.host.bridge.expectCall("presenceUpdate", helpers.TEST_JID_STR, "xa", 15, {'default': "test status", 'fr':'statut de test'}, helpers.TEST_PROFILE)
        self.presence.availableReceived(helpers.TEST_JID, 'xa', {None: "test status", 'fr':'statut de test'}, 15)

    def test_availableReceived_empty_statuses(self):
        self.host.bridge.expectCall("presenceUpdate", helpers.TEST_JID_STR, "xa", 15, {}, helpers.TEST_PROFILE)
        self.presence.availableReceived(helpers.TEST_JID, 'xa', None, 15)

    def test_unavailableReceived(self):
        self.host.bridge.expectCall("presenceUpdate", helpers.TEST_JID_STR, "unavailable", 0, {}, helpers.TEST_PROFILE)
        self.presence.unavailableReceived(helpers.TEST_JID, None)

    def test_subscribedReceived(self):
        self.host.bridge.expectCall("subscribe", "subscribed", helpers.TEST_JID.userhost(), helpers.TEST_PROFILE)
        self.presence.subscribedReceived(helpers.TEST_JID)
        
    def test_unsubscribedReceived(self):
        self.host.bridge.expectCall("subscribe", "unsubscribed", helpers.TEST_JID.userhost(), helpers.TEST_PROFILE)
        self.presence.unsubscribedReceived(helpers.TEST_JID)
    
    def test_subscribeReceived(self):
        self.host.bridge.expectCall("subscribe", "subscribe", helpers.TEST_JID.userhost(), helpers.TEST_PROFILE)
        self.presence.subscribeReceived(helpers.TEST_JID)
        
    def test_unsubscribeReceived(self):
        self.host.bridge.expectCall("subscribe", "unsubscribe", helpers.TEST_JID.userhost(), helpers.TEST_PROFILE)
        self.presence.unsubscribeReceived(helpers.TEST_JID)
    
