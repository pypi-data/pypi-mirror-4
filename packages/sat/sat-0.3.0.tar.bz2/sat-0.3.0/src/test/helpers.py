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

import __builtin__
from twisted.words.protocols.jabber.jid import JID

TEST_JID_STR = u"test@example.org/SàT" 
TEST_JID = JID(u"test@example.org/SàT") 
TEST_PROFILE = 'test_profile'

class DifferentArgsException(Exception):
    pass

class FakeSAT(object):
    """Class to simulate a SAT instance"""

    def __init__(self):
        self.bridge = FakeBridge()
        self.memory = FakeMemory()
        self.trigger = FakeTriggerManager() 


class FakeBridge(object):
    """Class to simulate and test bridge calls"""

    def expectCall(self, name, *check_args, **check_kwargs):
        def checkCall(*args, **kwargs):
            if args != check_args or kwargs != check_kwargs:
                print "\n\n--------------------"
                print "Args are not equals:"
                print "args\n----\n%s (sent)\n%s (wanted)" % (args, check_args)
                print "kwargs\n------\n%s (sent)\n%s (wanted)" % (kwargs, check_kwargs)
                print "--------------------\n\n"
                raise DifferentArgsException
            
        setattr(self, name, checkCall)


class FakeMemory(object):
    """Class to simulate and test memory object"""

    def getProfileName(self, profile_key):
        return profile_key

    def addToHistory(self, from_jid, to_jid, message, _type='chat', timestamp=None, profile=None):
        pass
    
    def addContact(self, contact_jid, attributes, groups, profile_key='@DEFAULT@'):
        pass
    
    def setPresenceStatus(self, contact_jid, show, priority, statuses, profile_key='@DEFAULT@'):
        pass
    
    def addWaitingSub(self, type, contact_jid, profile_key):
        pass
    
    def delWaitingSub(self, contact_jid, profile_key):
        pass

class FakeTriggerManager(object):

    def add(self, point_name, callback):
        pass
    
    def point(self, point_name, *args, **kwargs):
        """We always return true to continue the action"""
        return True

class FakeParent(object):
    def __init__(self):
        self.profile = 'test_profile'
        self.jid = TEST_JID

def _(text):
    return text

__builtin__.__dict__['_'] = _
