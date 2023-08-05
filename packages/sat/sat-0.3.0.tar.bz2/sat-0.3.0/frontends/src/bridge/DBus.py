#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
SAT communication bridge
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

from bridge_frontend import BridgeFrontend
import dbus
from logging import debug, error

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

const_INT_PREFIX = "org.goffi.SAT"  #Interface prefix
const_ERROR_PREFIX = const_INT_PREFIX+".error"
const_OBJ_PATH = '/org/goffi/SAT/bridge'
const_CORE_SUFFIX = ".core"
const_PLUGIN_SUFFIX = ".plugin"

class BridgeExceptionNoService(Exception):
    pass

class DBusBridgeFrontend(BridgeFrontend):
    def __init__(self):
        try:
            self.sessions_bus = dbus.SessionBus()
            self.db_object = self.sessions_bus.get_object(const_INT_PREFIX,
                                const_OBJ_PATH)
            self.db_core_iface = dbus.Interface(self.db_object,
                                dbus_interface=const_INT_PREFIX + const_CORE_SUFFIX)
            self.db_plugin_iface = dbus.Interface(self.db_object,
                                dbus_interface=const_INT_PREFIX + const_PLUGIN_SUFFIX)
        except dbus.exceptions.DBusException,e:
            if e._dbus_error_name=='org.freedesktop.DBus.Error.ServiceUnknown':
                raise BridgeExceptionNoService
            else:
                raise e
        #props = self.db_core_iface.getProperties()

    def register(self, functionName, handler, iface="core"):
        if iface == "core":
            self.db_core_iface.connect_to_signal(functionName, handler)
        elif iface == "plugin":
            self.db_plugin_iface.connect_to_signal(functionName, handler)
        else:
            error(_('Unknown interface'))

    def __getattribute__(self, name):
        """ usual __getattribute__ if the method exists, else try to find a plugin method """
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            # The attribute is not found, we try the plugin proxy to find the requested method

            def getPluginMethod(*args, **kwargs):
                # We first check if we have an async call. We detect this in two ways:
                #   - if we have the 'callback' and 'errback' keyword arguments
                #   - or if the last two arguments are callable

                async = False
                
                if kwargs:
                    if 'callback' in kwargs and 'errback' in kwargs:
                        async = True
                        _callback = kwargs.pop('callback')
                        _errback = kwargs.pop('errback')
                elif len(args)>=2 and callable(args[-1]) and callable(args[-2]):
                    async = True
                    args = list(args)
                    _errback = args.pop()
                    _callback = args.pop()
                        
                method = getattr(self.db_plugin_iface, name)
                
                if async:
                    kwargs['reply_handler'] = _callback
                    kwargs['error_handler'] = lambda err:_errback(err._dbus_error_name[len(const_ERROR_PREFIX)+1:])

                return method(*args, **kwargs)
                
            return getPluginMethod

    def addContact(self, entity_jid, profile_key="@DEFAULT@"):
        return self.db_core_iface.addContact(entity_jid, profile_key)

    def asyncConnect(self, profile_key="@DEFAULT@", callback=None, errback=None):
        return self.db_core_iface.asyncConnect(profile_key, reply_handler=callback, error_handler=lambda err:errback(err._dbus_error_name[len(const_ERROR_PREFIX)+1:]))

    def asyncCreateProfile(self, profile, callback=None, errback=None):
        return self.db_core_iface.asyncCreateProfile(profile, reply_handler=callback, error_handler=lambda err:errback(err._dbus_error_name[len(const_ERROR_PREFIX)+1:]))

    def asyncGetParamA(self, name, category, attribute="value", profile_key="@DEFAULT@", callback=None, errback=None):
        return unicode(self.db_core_iface.asyncGetParamA(name, category, attribute, profile_key, reply_handler=callback, error_handler=lambda err:errback(err._dbus_error_name[len(const_ERROR_PREFIX)+1:])))

    def callMenu(self, category, name, menu_type, profile_key):
        return unicode(self.db_core_iface.callMenu(category, name, menu_type, profile_key))

    def confirmationAnswer(self, id, accepted, data, profile):
        return self.db_core_iface.confirmationAnswer(id, accepted, data, profile)

    def connect(self, profile_key="@DEFAULT@"):
        return self.db_core_iface.connect(profile_key)

    def createProfile(self, profile):
        return self.db_core_iface.createProfile(profile)

    def delContact(self, entity_jid, profile_key="@DEFAULT@"):
        return self.db_core_iface.delContact(entity_jid, profile_key)

    def deleteProfile(self, profile):
        return self.db_core_iface.deleteProfile(profile)

    def disconnect(self, profile_key="@DEFAULT@"):
        return self.db_core_iface.disconnect(profile_key)

    def getConfig(self, section, name):
        return unicode(self.db_core_iface.getConfig(section, name))

    def getContacts(self, profile_key="@DEFAULT@"):
        return self.db_core_iface.getContacts(profile_key)

    def getContactsFromGroup(self, group, profile_key="@DEFAULT@"):
        return self.db_core_iface.getContactsFromGroup(group, profile_key)

    def getEntityData(self, jid, keys, profile):
        return self.db_core_iface.getEntityData(jid, keys, profile)

    def getHistory(self, from_jid, to_jid, limit, between=True, profile="@NONE@", callback=None, errback=None):
        return self.db_core_iface.getHistory(from_jid, to_jid, limit, between, profile, reply_handler=callback, error_handler=lambda err:errback(err._dbus_error_name[len(const_ERROR_PREFIX)+1:]))

    def getLastResource(self, contact_jid, profile_key="@DEFAULT@"):
        return unicode(self.db_core_iface.getLastResource(contact_jid, profile_key))

    def getMenuHelp(self, category, name, menu_type):
        return unicode(self.db_core_iface.getMenuHelp(category, name, menu_type))

    def getMenus(self, ):
        return self.db_core_iface.getMenus()

    def getParamA(self, name, category, attribute="value", profile_key="@DEFAULT@"):
        return unicode(self.db_core_iface.getParamA(name, category, attribute, profile_key))

    def getParams(self, profile_key="@DEFAULT@", callback=None, errback=None):
        return unicode(self.db_core_iface.getParams(profile_key, reply_handler=callback, error_handler=lambda err:errback(err._dbus_error_name[len(const_ERROR_PREFIX)+1:])))

    def getParamsCategories(self, ):
        return self.db_core_iface.getParamsCategories()

    def getParamsForCategory(self, category, profile_key="@DEFAULT@", callback=None, errback=None):
        return unicode(self.db_core_iface.getParamsForCategory(category, profile_key, reply_handler=callback, error_handler=lambda err:errback(err._dbus_error_name[len(const_ERROR_PREFIX)+1:])))

    def getParamsUI(self, profile_key="@DEFAULT@", callback=None, errback=None):
        return unicode(self.db_core_iface.getParamsUI(profile_key, reply_handler=callback, error_handler=lambda err:errback(err._dbus_error_name[len(const_ERROR_PREFIX)+1:])))

    def getPresenceStatus(self, profile_key="@DEFAULT@"):
        return self.db_core_iface.getPresenceStatus(profile_key)

    def getProfileName(self, profile_key="@DEFAULT@"):
        return unicode(self.db_core_iface.getProfileName(profile_key))

    def getProfilesList(self, ):
        return self.db_core_iface.getProfilesList()

    def getProgress(self, id, profile):
        return self.db_core_iface.getProgress(id, profile)

    def getVersion(self, ):
        return unicode(self.db_core_iface.getVersion())

    def getWaitingConf(self, profile_key):
        return self.db_core_iface.getWaitingConf(profile_key)

    def getWaitingSub(self, profile_key="@DEFAULT@"):
        return self.db_core_iface.getWaitingSub(profile_key)

    def isConnected(self, profile_key="@DEFAULT@"):
        return self.db_core_iface.isConnected(profile_key)

    def launchAction(self, action_type, data, profile_key="@DEFAULT@"):
        return unicode(self.db_core_iface.launchAction(action_type, data, profile_key))

    def registerNewAccount(self, login, password, email, host, port=5222):
        return unicode(self.db_core_iface.registerNewAccount(login, password, email, host, port))

    def sendMessage(self, to_jid, message, subject='', mess_type="auto", profile_key="@DEFAULT@"):
        return self.db_core_iface.sendMessage(to_jid, message, subject, mess_type, profile_key)

    def setParam(self, name, value, category, profile_key="@DEFAULT@"):
        return self.db_core_iface.setParam(name, value, category, profile_key)

    def setPresence(self, to_jid='', show='', priority=0, statuses={}, profile_key="@DEFAULT@"):
        return self.db_core_iface.setPresence(to_jid, show, priority, statuses, profile_key)

    def subscription(self, sub_type, entity, profile_key="@DEFAULT@"):
        return self.db_core_iface.subscription(sub_type, entity, profile_key)

    def updateContact(self, entity_jid, name, groups, profile_key="@DEFAULT@"):
        return self.db_core_iface.updateContact(entity_jid, name, groups, profile_key)


#methods from plugins
    
    def joinMUC(self, room_jid, nick, options, profile_key):
        if options == None:
            options = [('', '')] #XXX: we have to do this awful hack because python dbus need to guess the signature
        return self.db_plugin_iface.joinMUC(room_jid, nick, options, profile_key)
    
    def gatewayRegister(self, action, target, data, profile_key):
        if data == None:
            data = [('', '')] #XXX: we have to do this awful hack because python dbus need to guess the signature
        return self.db_plugin_iface.gatewayRegister(action, target, data, profile_key)