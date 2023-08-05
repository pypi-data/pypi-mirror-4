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

##METHODS_PART##

#methods from plugins
    
    def joinMUC(self, room_jid, nick, options, profile_key):
        if options == None:
            options = [('', '')] #XXX: we have to do this awful hack because python dbus need to guess the signature
        return self.db_plugin_iface.joinMUC(room_jid, nick, options, profile_key)
    
    def gatewayRegister(self, action, target, data, profile_key):
        if data == None:
            data = [('', '')] #XXX: we have to do this awful hack because python dbus need to guess the signature
        return self.db_plugin_iface.gatewayRegister(action, target, data, profile_key)
