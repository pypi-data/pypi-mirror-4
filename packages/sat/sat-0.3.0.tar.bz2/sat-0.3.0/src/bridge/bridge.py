#!/usr/bin/python
#-*- coding: utf-8 -*-

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

from logging import debug, info, error

class Bridge(object):
    def __init__(self):
        info ("Bridge initialization")

    ##signals
    def newContact(self, contact): 
        raise NotImplementedError

    def newMessage(self, from_jid, msg, type='chat'):
        raise NotImplementedError

    def presenceUpdate(self, type, jid, show, status, priority):
        raise NotImplementedError

    def paramUpdate(self, name, value):
        raise NotImplementedError


    ##methods
    def connect(self):
        raise NotImplementedError

    def getContacts(self):
        raise NotImplementedError
    
    def getPresenceStatus(self):
        raise NotImplementedError

    def sendMessage(self):
        raise NotImplementedError

    def setPresence(self, to="", type="", show="", status="", priority=0):
        raise NotImplementedError

    def setParam(self, name, value, namespace):
        raise NotImplementedError
        
    def getParam(self, name, namespace):
        raise NotImplementedError

    def getParams(self, namespace):
        raise NotImplementedError
    
    def getHistory(self, from_jid, to_jid, size):
        raise NotImplementedError
