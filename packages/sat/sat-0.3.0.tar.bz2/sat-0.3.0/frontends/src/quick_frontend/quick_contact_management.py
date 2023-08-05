#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
helper class for making a SAT frontend
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

from logging import debug, info, warning, error
from sat.tools.jid  import JID
import pdb


class QuickContactManagement():
    """This helper class manage the contacts and ease the use of nicknames and shortcuts"""
    ### FIXME: is SàT a better place for all this stuff ??? ###

    def __init__(self):
        self.__contactlist = {}

    def __contains__(self, entity):
        return entity.short in self.__contactlist

    def clear(self):
        """Clear all the contact list"""
        self.__contactlist.clear()

    def add(self, entity):
        """Add contact to the list, update resources"""
        if not self.__contactlist.has_key(entity.short):
            self.__contactlist[entity.short] = {'resources':[]}
        if not entity.resource:
            return
        if entity.resource in self.__contactlist[entity.short]['resources']:
            self.__contactlist[entity.short]['resources'].remove(entity.resource)
        self.__contactlist[entity.short]['resources'].append(entity.resource)
   
    def getContFromGroup(self, group):
        """Return all contacts which are in given group"""
        result = []
        for contact in self.__contactlist:
            if self.__contactlist[contact].has_key('groups'):
                if group in self.__contactlist[contact]['groups']:
                    result.append(JID(contact))
        return result

    def getAttr(self, entity, name):
        """Return a specific attribute of contact, or all attributes
        @param entity: jid of the contact
        @param name: name of the attribute
        @return: asked attribute"""
        if self.__contactlist.has_key(entity.short):
            if name == 'status':  #FIXME: for the moment, we only use the first status
                if self.__contactlist[entity.short]['statuses']:
                    return self.__contactlist[entity.short]['statuses'].values()[0]
            if self.__contactlist[entity.short].has_key(name):
                return self.__contactlist[entity.short][name]
        else:
            debug(_('Trying to get attribute for an unknown contact'))
        return None
    
    def isConnected(self, entity):
        """Tell if the contact is online"""
        return self.__contactlist.has_key(entity.short)

    def remove(self, entity):
        """remove resource. If no more resource is online or is no resource is specified, contact is deleted"""
        try:
            if entity.resource:
                self.__contactlist[entity.short]['resources'].remove(entity.resource)
            if not entity.resource or not self.__contactlist[entity.short]['resources']:
                #no more resource available: the contact seems really disconnected
                del self.__contactlist[entity.short]
        except KeyError:
            error(_('INTERNAL ERROR: Key error'))
            raise

    def update(self, entity, key, value):
        """Update attribute of contact
        @param entity: jid of the contact
        @param key: name of the attribute
        @param value: value of the attribute
        """
        if self.__contactlist.has_key(entity.short):
            self.__contactlist[entity.short][key] = value
        else:
            debug (_('Trying to update an unknown contact: %s'), entity.short)

    def get_full(self, entity):
        return entity.short+'/'+self.__contactlist[entity.short]['resources'][-1]
        
