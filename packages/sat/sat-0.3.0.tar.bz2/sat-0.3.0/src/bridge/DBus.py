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


from bridge import Bridge
import dbus
import dbus.service
import dbus.mainloop.glib
import inspect
from logging import debug, info, error
from twisted.internet.defer import Deferred

const_INT_PREFIX = "org.goffi.SAT"  #Interface prefix
const_ERROR_PREFIX = const_INT_PREFIX+".error"
const_OBJ_PATH = '/org/goffi/SAT/bridge'
const_CORE_SUFFIX = ".core"
const_PLUGIN_SUFFIX = ".plugin"

class ParseError(Exception):
    pass

class MethodNotRegistered(dbus.DBusException):
    _dbus_error_name = const_ERROR_PREFIX + ".MethodNotRegistered"

class InternalError(dbus.DBusException):
    _dbus_error_name = const_ERROR_PREFIX + ".InternalError"

class AsyncNotDeferred(dbus.DBusException):
    _dbus_error_name = const_ERROR_PREFIX + ".AsyncNotDeferred"

class DeferredNotAsync(dbus.DBusException):
    _dbus_error_name = const_ERROR_PREFIX + ".DeferredNotAsync"

class GenericException(dbus.DBusException):
    def __init__(self, twisted_error):
        super(GenericException,self).__init__()
        mess = twisted_error.getErrorMessage()
        self._dbus_error_name = const_ERROR_PREFIX+"."+ (mess or str(twisted_error.__class__))

class DbusObject(dbus.service.Object):

    def __init__(self, bus, path):
        dbus.service.Object.__init__(self, bus, path)
        debug("Init DbusObject...")
        self.cb={}

    def register(self, name, cb):
        self.cb[name]=cb

    def _callback(self, name, *args, **kwargs):
        """call the callback if it exists, raise an exception else
        if the callback return a deferred, use async methods"""
        if not name in self.cb:
            raise MethodNotRegistered

        if "callback" in kwargs:
            #we must have errback too
            if not "errback" in kwargs:
                error("errback is missing in method call [%s]" % name)
                raise InternalError
            callback = kwargs.pop("callback")
            errback = kwargs.pop("errback")
            async = True
        else:
            async = False
        result = self.cb[name](*args, **kwargs)
        if async:
            if not isinstance(result, Deferred):
                error("Asynchronous method [%s] does not return a Deferred." % name)
                raise AsyncNotDeferred
            result.addCallback(lambda result: callback() if result==None else callback(result))
            result.addErrback(lambda err:errback(GenericException(err)))
        else:
            if isinstance(result, Deferred):
                error("Synchronous method [%s] return a Deferred." % name)
                raise DeferredNotAsync
            return result

    ### signals ###    

    @dbus.service.signal(const_INT_PREFIX+const_PLUGIN_SUFFIX,
                         signature='')
    def dummySignal(self):
        #FIXME: workaround for addSignal (doesn't work if one method doensn't
        #       already exist for plugins), probably missing some initialisation, need
        #       further investigations
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='ssa{ss}s')
    def actionResult(self, answer_type, id, data, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='ssa{sa{ss}}s')
    def actionResultExt(self, answer_type, id, data, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='ssa{ss}s')
    def askConfirmation(self, id, conf_type, data, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='s')
    def connected(self, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='ss')
    def connectionError(self, error_type, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='ss')
    def contactDeleted(self, entity_jid, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='s')
    def disconnected(self, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='ssss')
    def entityDataUpdated(self, jid, name, value, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='ssss')
    def newAlert(self, message, title, alert_type, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='sa{ss}ass')
    def newContact(self, contact_jid, attributes, groups, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='ssssa{ss}s')
    def newMessage(self, from_jid, message, mess_type, to_jid, extra, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='ssss')
    def paramUpdate(self, name, value, category, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='ssia{ss}s')
    def presenceUpdate(self, entity_jid, show, priority, statuses, profile):
        pass

    @dbus.service.signal(const_INT_PREFIX+const_CORE_SUFFIX,
                         signature='sss')
    def subscribe(self, sub_type, entity_jid, profile):
        pass


    ### methods ###    
    
    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ss', out_signature='',
                         async_callbacks=None)
    def addContact(self, entity_jid, profile_key="@DEFAULT@"):
        return self._callback("addContact", unicode(entity_jid), unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='',
                         async_callbacks=('callback', 'errback'))
    def asyncConnect(self, profile_key="@DEFAULT@", callback=None, errback=None):
        return self._callback("asyncConnect", unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='',
                         async_callbacks=('callback', 'errback'))
    def asyncCreateProfile(self, profile, callback=None, errback=None):
        return self._callback("asyncCreateProfile", unicode(profile), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ssss', out_signature='s',
                         async_callbacks=('callback', 'errback'))
    def asyncGetParamA(self, name, category, attribute="value", profile_key="@DEFAULT@", callback=None, errback=None):
        return self._callback("asyncGetParamA", unicode(name), unicode(category), unicode(attribute), unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ssss', out_signature='s',
                         async_callbacks=None)
    def callMenu(self, category, name, menu_type, profile_key):
        return self._callback("callMenu", unicode(category), unicode(name), unicode(menu_type), unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='sba{ss}s', out_signature='',
                         async_callbacks=None)
    def confirmationAnswer(self, id, accepted, data, profile):
        return self._callback("confirmationAnswer", unicode(id), accepted, data, unicode(profile))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='',
                         async_callbacks=None)
    def connect(self, profile_key="@DEFAULT@"):
        return self._callback("connect", unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='i',
                         async_callbacks=None)
    def createProfile(self, profile):
        return self._callback("createProfile", unicode(profile))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ss', out_signature='',
                         async_callbacks=None)
    def delContact(self, entity_jid, profile_key="@DEFAULT@"):
        return self._callback("delContact", unicode(entity_jid), unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='i',
                         async_callbacks=None)
    def deleteProfile(self, profile):
        return self._callback("deleteProfile", unicode(profile))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='',
                         async_callbacks=None)
    def disconnect(self, profile_key="@DEFAULT@"):
        return self._callback("disconnect", unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ss', out_signature='s',
                         async_callbacks=None)
    def getConfig(self, section, name):
        return self._callback("getConfig", unicode(section), unicode(name))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='a(sa{ss}as)',
                         async_callbacks=None)
    def getContacts(self, profile_key="@DEFAULT@"):
        return self._callback("getContacts", unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ss', out_signature='as',
                         async_callbacks=None)
    def getContactsFromGroup(self, group, profile_key="@DEFAULT@"):
        return self._callback("getContactsFromGroup", unicode(group), unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='sass', out_signature='a{ss}',
                         async_callbacks=None)
    def getEntityData(self, jid, keys, profile):
        return self._callback("getEntityData", unicode(jid), keys, unicode(profile))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ssibs', out_signature='a(dssss)',
                         async_callbacks=('callback', 'errback'))
    def getHistory(self, from_jid, to_jid, limit, between=True, profile="@NONE@", callback=None, errback=None):
        return self._callback("getHistory", unicode(from_jid), unicode(to_jid), limit, between, unicode(profile), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ss', out_signature='s',
                         async_callbacks=None)
    def getLastResource(self, contact_jid, profile_key="@DEFAULT@"):
        return self._callback("getLastResource", unicode(contact_jid), unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='sss', out_signature='s',
                         async_callbacks=None)
    def getMenuHelp(self, category, name, menu_type):
        return self._callback("getMenuHelp", unicode(category), unicode(name), unicode(menu_type))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='', out_signature='a(sss)',
                         async_callbacks=None)
    def getMenus(self, ):
        return self._callback("getMenus", )

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ssss', out_signature='s',
                         async_callbacks=None)
    def getParamA(self, name, category, attribute="value", profile_key="@DEFAULT@"):
        return self._callback("getParamA", unicode(name), unicode(category), unicode(attribute), unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='s',
                         async_callbacks=('callback', 'errback'))
    def getParams(self, profile_key="@DEFAULT@", callback=None, errback=None):
        return self._callback("getParams", unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='', out_signature='as',
                         async_callbacks=None)
    def getParamsCategories(self, ):
        return self._callback("getParamsCategories", )

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ss', out_signature='s',
                         async_callbacks=('callback', 'errback'))
    def getParamsForCategory(self, category, profile_key="@DEFAULT@", callback=None, errback=None):
        return self._callback("getParamsForCategory", unicode(category), unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='s',
                         async_callbacks=('callback', 'errback'))
    def getParamsUI(self, profile_key="@DEFAULT@", callback=None, errback=None):
        return self._callback("getParamsUI", unicode(profile_key), callback=callback, errback=errback)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='a{sa{s(sia{ss})}}',
                         async_callbacks=None)
    def getPresenceStatus(self, profile_key="@DEFAULT@"):
        return self._callback("getPresenceStatus", unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='s',
                         async_callbacks=None)
    def getProfileName(self, profile_key="@DEFAULT@"):
        return self._callback("getProfileName", unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='', out_signature='as',
                         async_callbacks=None)
    def getProfilesList(self, ):
        return self._callback("getProfilesList", )

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ss', out_signature='a{ss}',
                         async_callbacks=None)
    def getProgress(self, id, profile):
        return self._callback("getProgress", unicode(id), unicode(profile))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='', out_signature='s',
                         async_callbacks=None)
    def getVersion(self, ):
        return self._callback("getVersion", )

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='a(ssa{ss})',
                         async_callbacks=None)
    def getWaitingConf(self, profile_key):
        return self._callback("getWaitingConf", unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='a{ss}',
                         async_callbacks=None)
    def getWaitingSub(self, profile_key="@DEFAULT@"):
        return self._callback("getWaitingSub", unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='s', out_signature='b',
                         async_callbacks=None)
    def isConnected(self, profile_key="@DEFAULT@"):
        return self._callback("isConnected", unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='sa{ss}s', out_signature='s',
                         async_callbacks=None)
    def launchAction(self, action_type, data, profile_key="@DEFAULT@"):
        return self._callback("launchAction", unicode(action_type), data, unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ssssi', out_signature='s',
                         async_callbacks=None)
    def registerNewAccount(self, login, password, email, host, port=5222):
        return self._callback("registerNewAccount", unicode(login), unicode(password), unicode(email), unicode(host), port)

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='sssss', out_signature='',
                         async_callbacks=None)
    def sendMessage(self, to_jid, message, subject='', mess_type="auto", profile_key="@DEFAULT@"):
        return self._callback("sendMessage", unicode(to_jid), unicode(message), unicode(subject), unicode(mess_type), unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ssss', out_signature='',
                         async_callbacks=None)
    def setParam(self, name, value, category, profile_key="@DEFAULT@"):
        return self._callback("setParam", unicode(name), unicode(value), unicode(category), unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ssia{ss}s', out_signature='',
                         async_callbacks=None)
    def setPresence(self, to_jid='', show='', priority=0, statuses={}, profile_key="@DEFAULT@"):
        return self._callback("setPresence", unicode(to_jid), unicode(show), priority, statuses, unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='sss', out_signature='',
                         async_callbacks=None)
    def subscription(self, sub_type, entity, profile_key="@DEFAULT@"):
        return self._callback("subscription", unicode(sub_type), unicode(entity), unicode(profile_key))

    @dbus.service.method(const_INT_PREFIX+const_CORE_SUFFIX,
                         in_signature='ssass', out_signature='',
                         async_callbacks=None)
    def updateContact(self, entity_jid, name, groups, profile_key="@DEFAULT@"):
        return self._callback("updateContact", unicode(entity_jid), unicode(name), groups, unicode(profile_key))

    
    def __attributes(self, in_sign):
        """Return arguments to user given a in_sign
        @param in_sign: in_sign in the short form (using s,a,i,b etc)
        @return: list of arguments that correspond to a in_sign (e.g.: "sss" return "arg1, arg2, arg3")""" 
        i=0
        idx=0
        attr=[]
        while i<len(in_sign):
            if in_sign[i] not in ['b','y','n','i','x','q','u','t','d','s','a']:
                raise ParseError("Unmanaged attribute type [%c]" % in_sign[i])

            attr.append("arg_%i" % idx)
            idx+=1

            if in_sign[i] == 'a':
                i+=1
                if in_sign[i]!='{' and in_sign[i]!='(': #FIXME: must manage tuples out of arrays
                    i+=1
                    continue #we have a simple type for the array
                opening_car = in_sign[i]
                assert(opening_car in ['{','('])
                closing_car = '}' if opening_car == '{' else ')'
                opening_count = 1
                while (True): #we have a dict or a list of tuples
                    i+=1
                    if i>=len(in_sign):
                        raise ParseError("missing }")
                    if in_sign[i] == opening_car:
                        opening_count+=1
                    if in_sign[i] == closing_car:
                        opening_count-=1
                        if opening_count == 0:
                            break
            i+=1
        return attr

    def addMethod(self, name, int_suffix, in_sign, out_sign, method, async=False):
        """Dynamically add a method to Dbus Bridge"""
        inspect_args = inspect.getargspec(method)

        _arguments = inspect_args.args
        _defaults = list(inspect_args.defaults or [])
        
        if inspect.ismethod(method):
            #if we have a method, we don't want the first argument (usually 'self')
            del(_arguments[0])

        #first arguments are for the _callback method
        arguments_callback = ', '.join([repr(name)] + ((_arguments + ['callback=callback','errback=errback']) if async else _arguments))
        
        if async:
            _arguments.extend(['callback','errback'])
            _defaults.extend([None, None])
        
        
        #now we create a second list with default values
        for i in range(1, len(_defaults)+1):
            _arguments[-i] = "%s = %s" % (_arguments[-i], repr(_defaults[-i]))

        arguments_defaults =  ', '.join(_arguments)

        code = compile ('def %(name)s (self,%(arguments_defaults)s): return self._callback(%(arguments_callback)s)' %
                        {'name':name, 'arguments_defaults':arguments_defaults, 'arguments_callback':arguments_callback}, '<DBus bridge>','exec')
        exec (code) #FIXME: to the same thing in a cleaner way, without compile/exec
        method = locals()[name]
        async_callbacks = ('callback', 'errback') if async else None
        setattr(DbusObject, name, dbus.service.method(
            const_INT_PREFIX+int_suffix, in_signature=in_sign, out_signature=out_sign,
            async_callbacks=async_callbacks)(method))
        function = getattr(self, name)
        func_table = self._dbus_class_table[self.__class__.__module__ + '.' + self.__class__.__name__][function._dbus_interface]
        func_table[function.__name__] = function #Needed for introspection
    
    def addSignal(self, name, int_suffix, signature, doc={}):
        """Dynamically add a signal to Dbus Bridge"""
        attributes = ', '.join(self.__attributes(signature))
        #TODO: use doc parameter to name attributes

        #code = compile ('def '+name+' (self,'+attributes+'): debug ("'+name+' signal")', '<DBus bridge>','exec') #XXX: the debug is too annoying with xmllog
        code = compile ('def '+name+' (self,'+attributes+'): pass', '<DBus bridge>','exec')
        exec (code)
        signal = locals()[name]
        setattr(DbusObject, name, dbus.service.signal(
            const_INT_PREFIX+int_suffix, signature=signature)(signal))
        function = getattr(self, name)
        func_table = self._dbus_class_table[self.__class__.__module__ + '.' + self.__class__.__name__][function._dbus_interface]
        func_table[function.__name__] = function #Needed for introspection

class DBusBridge(Bridge):
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        Bridge.__init__(self)
        info ("Init DBus...")
        self.session_bus = dbus.SessionBus()
        self.dbus_name = dbus.service.BusName(const_INT_PREFIX, self.session_bus)
        self.dbus_bridge = DbusObject(self.session_bus, const_OBJ_PATH)

    def actionResult(self, answer_type, id, data, profile):
        self.dbus_bridge.actionResult(answer_type, id, data, profile)

    def actionResultExt(self, answer_type, id, data, profile):
        self.dbus_bridge.actionResultExt(answer_type, id, data, profile)

    def askConfirmation(self, id, conf_type, data, profile):
        self.dbus_bridge.askConfirmation(id, conf_type, data, profile)

    def connected(self, profile):
        self.dbus_bridge.connected(profile)

    def connectionError(self, error_type, profile):
        self.dbus_bridge.connectionError(error_type, profile)

    def contactDeleted(self, entity_jid, profile):
        self.dbus_bridge.contactDeleted(entity_jid, profile)

    def disconnected(self, profile):
        self.dbus_bridge.disconnected(profile)

    def entityDataUpdated(self, jid, name, value, profile):
        self.dbus_bridge.entityDataUpdated(jid, name, value, profile)

    def newAlert(self, message, title, alert_type, profile):
        self.dbus_bridge.newAlert(message, title, alert_type, profile)

    def newContact(self, contact_jid, attributes, groups, profile):
        self.dbus_bridge.newContact(contact_jid, attributes, groups, profile)

    def newMessage(self, from_jid, message, mess_type, to_jid, extra, profile):
        self.dbus_bridge.newMessage(from_jid, message, mess_type, to_jid, extra, profile)

    def paramUpdate(self, name, value, category, profile):
        self.dbus_bridge.paramUpdate(name, value, category, profile)

    def presenceUpdate(self, entity_jid, show, priority, statuses, profile):
        self.dbus_bridge.presenceUpdate(entity_jid, show, priority, statuses, profile)

    def subscribe(self, sub_type, entity_jid, profile):
        self.dbus_bridge.subscribe(sub_type, entity_jid, profile)


    def register(self, name, callback):
        debug("registering DBus bridge method [%s]", name)
        self.dbus_bridge.register(name, callback)

    def addMethod(self, name, int_suffix, in_sign, out_sign, method, async=False, doc={}):
        """Dynamically add a method to Dbus Bridge"""
        #FIXME: doc parameter is kept only temporary, the time to remove it from calls
        print ("Adding method [%s] to DBus bridge" % name)
        self.dbus_bridge.addMethod(name, int_suffix, in_sign, out_sign, method, async)
        self.register(name, method)

    def addSignal(self, name, int_suffix, signature, doc={}):
        self.dbus_bridge.addSignal(name, int_suffix, signature, doc)
        setattr(DBusBridge, name, getattr(self.dbus_bridge, name))
