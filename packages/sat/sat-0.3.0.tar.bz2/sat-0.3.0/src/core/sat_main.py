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

from twisted.application import service
from twisted.internet import defer

from twisted.words.protocols.jabber import jid, xmlstream
from twisted.words.xish import domish

from twisted.internet import reactor

from wokkel import compat
from wokkel.xmppim import RosterItem

from sat.bridge.DBus import DBusBridge
import logging
from logging import debug, info, warning, error

import sys
import os.path

from sat.core.default_config import CONST
from sat.core import xmpp
from sat.core.exceptions import ProfileUnknownError, UnknownEntityError, ProfileNotInCacheError
from sat.memory.memory import Memory
from sat.tools.xml_tools import tupleList2dataForm
from sat.tools.misc import TriggerManager
from glob import glob

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler


### logging configuration FIXME: put this elsewhere ###
logging.basicConfig(level=logging.DEBUG,
                    format='%(message)s')
###


sat_id = 0

def sat_next_id():
    global sat_id
    sat_id+=1
    return "sat_id_"+str(sat_id)

class SAT(service.Service):
   
    def get_next_id(self):
        return sat_next_id()

    def get_const(self, name):
        """Return a constant"""
        try:
            _const = os.environ['SAT_CONST_%s' % name]
            if _const:
                debug(_("Constant %(name)s overrided with [%(value)s]") % {'name':name, 'value': _const})
                return _const
        except KeyError:
            pass
        if not CONST.has_key(name):
            error(_('Trying to access an undefined constant'))
            raise Exception
        return CONST[name]

    def set_const(self, name, value):
        """Save a constant"""
        if CONST.has_key(name):
            error(_('Trying to redefine a constant'))
            raise Exception  
        CONST[name] = value
    
    def __init__(self):
        #TODO: standardize callback system
        
        self.__general_cb_map = {}  #callback called for general reasons (key = name) 
        self.__private_data = {}  #used for internal callbacks (key = id)
        self.profiles = {}
        self.plugins = {}
        self.menus = {} #used to know which new menus are wanted by plugins
        
        self.memory=Memory(self)
        
        local_dir = self.memory.getConfig('', 'local_dir')
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)

        self.trigger = TriggerManager() #trigger are used to change SàT behaviour 
        
        self.bridge=DBusBridge()
        self.bridge.register("getVersion", lambda: self.get_const('client_version'))
        self.bridge.register("getProfileName", self.memory.getProfileName)
        self.bridge.register("getProfilesList", self.memory.getProfilesList)
        self.bridge.register("getEntityData", lambda _jid, keys, profile: self.memory.getEntityData(jid.JID(_jid), keys, profile))
        self.bridge.register("createProfile", self.memory.createProfile)
        self.bridge.register("asyncCreateProfile", self.memory.asyncCreateProfile)
        self.bridge.register("deleteProfile", self.memory.deleteProfile)
        self.bridge.register("registerNewAccount", self.registerNewAccount)
        self.bridge.register("connect", self.connect)
        self.bridge.register("asyncConnect", self.asyncConnect)
        self.bridge.register("disconnect", self.disconnect)
        self.bridge.register("getContacts", self.getContacts)
        self.bridge.register("getContactsFromGroup", self.getContactsFromGroup)
        self.bridge.register("getLastResource", self.memory.getLastResource)
        self.bridge.register("getPresenceStatus", self.memory.getPresenceStatus)
        self.bridge.register("getWaitingSub", self.memory.getWaitingSub)
        self.bridge.register("getWaitingConf", self.getWaitingConf)
        self.bridge.register("sendMessage", self.sendMessage)
        self.bridge.register("getConfig", self.memory.getConfig)
        self.bridge.register("setParam", self.setParam)
        self.bridge.register("getParamA", self.memory.getStringParamA)
        self.bridge.register("asyncGetParamA", self.memory.asyncGetStringParamA)
        self.bridge.register("getParamsUI", self.memory.getParamsUI)
        self.bridge.register("getParams", self.memory.getParams)
        self.bridge.register("getParamsForCategory", self.memory.getParamsForCategory)
        self.bridge.register("getParamsCategories", self.memory.getParamsCategories)
        self.bridge.register("getHistory", self.memory.getHistory)
        self.bridge.register("setPresence", self.setPresence)
        self.bridge.register("subscription", self.subscription)
        self.bridge.register("addContact", self.addContact)
        self.bridge.register("updateContact", self.updateContact)
        self.bridge.register("delContact", self.delContact)
        self.bridge.register("isConnected", self.isConnected)
        self.bridge.register("launchAction", self.launchAction)
        self.bridge.register("confirmationAnswer", self.confirmationAnswer)
        self.bridge.register("getProgress", self.getProgress)
        self.bridge.register("getMenus", self.getMenus)
        self.bridge.register("getMenuHelp", self.getMenuHelp)
        self.bridge.register("callMenu", self.callMenu)
    
        self.memory.initialized.addCallback(self._postMemoryInit) 

    def _postMemoryInit(self, ignore):
        """Method called after memory initialization is done"""
        info(_("Memory initialised"))
        self._import_plugins()


    def _import_plugins(self):
        """Import all plugins found in plugins directory"""
        import sat.plugins
        plugins_path = os.path.dirname(sat.plugins.__file__) 
        plug_lst = [os.path.splitext(plugin)[0] for plugin in map(os.path.basename,glob(os.path.join(plugins_path,"plugin*.py")))]
        __plugins_to_import = {} #plugins we still have to import
        for plug in plug_lst:
            plugin_path = 'sat.plugins.'+plug
            __import__(plugin_path)
            mod = sys.modules[plugin_path]
            plugin_info = mod.PLUGIN_INFO
            __plugins_to_import[plugin_info['import_name']] = (plugin_path, mod, plugin_info)
        while True:
            self._import_plugins_from_dict(__plugins_to_import)
            if not __plugins_to_import:
                break

    def _import_plugins_from_dict(self, plugins_to_import, import_name=None):
        """Recursively import and their dependencies in the right order
        @param plugins_to_import: dict where key=import_name and values= (plugin_path, module, plugin_info)"""
        if self.plugins.has_key(import_name):
            debug('Plugin [%s] already imported, passing' % import_name)
            return
        if not import_name:
            import_name,(plugin_path, mod, plugin_info) = plugins_to_import.popitem()
        else:
            if not import_name in plugins_to_import:
                raise ImportError(_('Dependency plugin not found: [%s]') % import_name)
            plugin_path, mod, plugin_info = plugins_to_import.pop(import_name)
        dependencies = plugin_info.setdefault("dependencies",[])
        for dependency in dependencies:
            if not self.plugins.has_key(dependency):
                debug('Recursively import dependency of [%s]: [%s]' % (import_name, dependency))
                self._import_plugins_from_dict(plugins_to_import, dependency)
        info (_("importing plugin: %s"), plugin_info['name'])
        self.plugins[import_name] = getattr(mod, plugin_info['main'])(self)
        if plugin_info.has_key('handler') and plugin_info['handler'] == 'yes':
            self.plugins[import_name].is_handler = True
        else:
            self.plugins[import_name].is_handler = False
        #TODO: test xmppclient presence and register handler parent

    
    def connect(self, profile_key = '@DEFAULT@'):
        """Connect to jabber server"""
        self.asyncConnect(profile_key)
    
    def asyncConnect(self, profile_key = '@DEFAULT@'):
        """Connect to jabber server with asynchronous reply
        @param profile_key: %(doc_profile)s
        """

        profile = self.memory.getProfileName(profile_key)
        if not profile:
            error (_('Trying to connect a non-exsitant profile'))
            raise ProfileUnknownError(profile_key)
        
        if (self.isConnected(profile)):
            info(_("already connected !"))
            return defer.succeed("None")

        def afterMemoryInit(ignore):
            """This part must be called when we have loaded individual parameters from memory"""
            try:
                port = int(self.memory.getParamA("Port", "Connection", profile_key = profile))
            except ValueError:
                error(_("Can't parse port value, using default value"))
                port = 5222
            current = self.profiles[profile] = xmpp.SatXMPPClient(self, profile,
                jid.JID(self.memory.getParamA("JabberID", "Connection", profile_key = profile), profile),
                self.memory.getParamA("Password", "Connection", profile_key = profile),
                self.memory.getParamA("Server", "Connection", profile_key = profile), 
                port)

            current.messageProt = xmpp.SatMessageProtocol(self)
            current.messageProt.setHandlerParent(current)
            
            current.roster = xmpp.SatRosterProtocol(self)
            current.roster.setHandlerParent(current)

            current.presence = xmpp.SatPresenceProtocol(self)
            current.presence.setHandlerParent(current)

            current.fallBack = xmpp.SatFallbackHandler(self)
            current.fallBack.setHandlerParent(current)

            current.versionHandler = xmpp.SatVersionHandler(self.get_const('client_name'),
                                                         self.get_const('client_version'))
            current.versionHandler.setHandlerParent(current)

            debug (_("setting plugins parents"))
            
            for plugin in self.plugins.iteritems():
                if plugin[1].is_handler:
                    plugin[1].getHandler(profile).setHandlerParent(current)
                connected_cb = getattr(plugin[1], "profileConnected", None)
                if connected_cb:
                    connected_cb(profile)

            current.startService()

            d = current.getConnectionDeferred()
            d.addCallback(lambda x: current.roster.got_roster) #we want to be sure that we got the roster
            return d

        self.memory.startProfileSession(profile)
        return self.memory.loadIndividualParams(profile).addCallback(afterMemoryInit)

    def disconnect(self, profile_key):
        """disconnect from jabber server"""
        if (not self.isConnected(profile_key)):
            info(_("not connected !"))
            return
        profile = self.memory.getProfileName(profile_key)
        info(_("Disconnecting..."))
        self.profiles[profile].stopService()
        for plugin in self.plugins.iteritems():
            disconnected_cb = getattr(plugin[1], "profileDisconnected", None)
            if disconnected_cb:
                disconnected_cb(profile)

    def getContacts(self, profile_key):
        client = self.getClient(profile_key)
        if not client:
            raise ProfileUnknownError(_('Asking contacts for a non-existant profile'))
        ret = []
        for item in client.roster.getItems(): #we get all items for client's roster
            #and convert them to expected format
            attr = client.roster.getAttributes(item)
            ret.append([item.jid.userhost(), attr, item.groups])
        return ret

    def getContactsFromGroup(self, group, profile_key):
        client = self.getClient(profile_key)
        if not client:
            raise ProfileUnknownError(_("Asking group's contacts for a non-existant profile"))
        return client.roster.getJidsFromGroup(group)

    def purgeClient(self, profile):
        """Remove reference to a profile client and purge cache
        the garbage collector can then free the memory"""
        try:
            del self.profiles[profile]
        except KeyError:
            error(_("Trying to remove reference to a client not referenced"))
        self.memory.purgeProfileSession(profile)

    def startService(self):
        info("Salut à toi ô mon frère !")
        #TODO: manage autoconnect
        #self.connect()
    
    def stopService(self):
        self.memory.save()
        info("Salut aussi à Rantanplan")

    def run(self):
        debug(_("running app"))
        reactor.run()
    
    def stop(self):
        debug(_("stopping app"))
        reactor.stop()
        
    ## Misc methods ##
   
    def getJidNStream(self, profile_key):
        """Convenient method to get jid and stream from profile key
        @return: tuple (jid, xmlstream) from profile, can be None"""
        profile = self.memory.getProfileName(profile_key)
        if not profile or not self.profiles[profile].isConnected():
            return (None, None)
        return (self.profiles[profile].jid, self.profiles[profile].xmlstream)

    def getClient(self, profile_key):
        """Convenient method to get client from profile key
        @return: client or None if it doesn't exist"""
        profile = self.memory.getProfileName(profile_key)
        if not profile:
            return None
        return self.profiles[profile]

    def registerNewAccount(self, login, password, email, server, port = 5222, id = None, profile_key = '@DEFAULT@'):
        """Connect to a server and create a new account using in-band registration"""
        profile = self.memory.getProfileName(profile_key)
        assert(profile)

        next_id = id or sat_next_id()  #the id is used to send server's answer
        serverRegistrer = xmlstream.XmlStreamFactory(xmpp.RegisteringAuthenticator(self, server, login, password, email, next_id, profile))
        connector = reactor.connectTCP(server, port, serverRegistrer)
        serverRegistrer.clientConnectionLost = lambda conn, reason: connector.disconnect()
        
        return next_id 

    def registerNewAccountCB(self, id, data, profile):
        user = jid.parse(self.memory.getParamA("JabberID", "Connection", profile_key=profile))[0]
        password = self.memory.getParamA("Password", "Connection", profile_key=profile)
        server = self.memory.getParamA("Server", "Connection", profile_key=profile)

        if not user or not password or not server:
            info (_('No user or server given'))
            #TODO: a proper error message must be sent to frontend
            self.actionResult(id, "ERROR", {'message':_("No user, password or server given, can't register new account.")}, profile)
            return

        confirm_id = sat_next_id()
        self.__private_data[confirm_id]=(id,profile)
    
        self.askConfirmation(confirm_id, "YES/NO",
            {"message":_("Are you sure to register new account [%(user)s] to server %(server)s ?") % {'user':user, 'server':server, 'profile':profile}},
            self.regisConfirmCB, profile)
        print ("===============+++++++++++ REGISTER NEW ACCOUNT++++++++++++++============")
        print "id=",id
        print "data=",data

    def regisConfirmCB(self, id, accepted, data, profile):
        print _("register Confirmation CB ! (%s)") % str(accepted)
        action_id,profile = self.__private_data[id]
        del self.__private_data[id]
        if accepted:
            user = jid.parse(self.memory.getParamA("JabberID", "Connection", profile_key=profile))[0]
            password = self.memory.getParamA("Password", "Connection", profile_key=profile)
            server = self.memory.getParamA("Server", "Connection", profile_key=profile)
            self.registerNewAccount(user, password, None, server, id=action_id)
        else:
            self.actionResult(action_id, "SUPPRESS", {}, profile)

    def submitForm(self, action, target, fields, profile_key):
        """submit a form
        @param target: target jid where we are submitting
        @param fields: list of tuples (name, value)
        @return: tuple: (id, deferred)
        """

        profile = self.memory.getProfileName(profile_key)
        assert(profile)
        to_jid = jid.JID(target)
        
        iq = compat.IQ(self.profiles[profile].xmlstream, 'set')
        iq["to"] = target
        iq["from"] = self.profiles[profile].jid.full()
        query = iq.addElement(('jabber:iq:register', 'query'))
        if action=='SUBMIT':
            form = tupleList2dataForm(fields)
            query.addChild(form.toElement())
        elif action=='CANCEL':
            query.addElement('remove')
        else:
            error (_("FIXME FIXME FIXME: Unmanaged action (%s) in submitForm") % action)
            raise NotImplementedError

        deferred = iq.send(target)
        return (iq['id'], deferred)

    ## Client management ##

    def setParam(self, name, value, category, profile_key):
        """set wanted paramater and notice observers"""
        info (_("setting param: %(name)s=%(value)s in category %(category)s") % {'name':name, 'value':value, 'category':category})
        self.memory.setParam(name, value, category, profile_key)

    def isConnected(self, profile_key):
        """Return connection status of profile
        @param profile_key: key_word or profile name to determine profile name
        @return True if connected
        """
        profile = self.memory.getProfileName(profile_key)
        if not profile:
            error (_('asking connection status for a non-existant profile'))
            return
        if not self.profiles.has_key(profile):
            return False
        return self.profiles[profile].isConnected()

    def launchAction(self, type, data, profile_key):
        """Launch a specific action asked by client
        @param type: action type (button)
        @param data: needed data to launch the action

        @return: action id for result, or empty string in case or error
        """
        profile = self.memory.getProfileName(profile_key)
        if not profile:
            error (_('trying to launch action with a non-existant profile'))
            raise Exception  #TODO: raise a proper exception
        if type=="button":
            try:
                cb_name = data['callback_id']
            except KeyError:
                error (_("Incomplete data"))
                return ""
            id = sat_next_id()
            self.callGeneralCB(cb_name, id, data, profile = profile)
            return id
        else:
            error (_("Unknown action type"))
            return ""


    ## jabber methods ##
   
    def getWaitingConf(self, profile_key=None):
        assert(profile_key)
        client = self.getClient(profile_key)
        if not client:
            raise ProfileNotInCacheError
        ret = []
        for conf_id in client._waiting_conf:
            conf_type, data = client._waiting_conf[conf_id][:2]
            ret.append((conf_id, conf_type, data))
        return ret
    
    def sendMessage(self, to, msg, subject=None, mess_type='auto', profile_key='@DEFAULT@'):
        #FIXME: check validity of recipient
        profile = self.memory.getProfileName(profile_key)
        assert(profile)
        client = self.profiles[profile]
        current_jid = client.jid
        mess_data = { #we put data in a dict, so trigger methods can change them 
                      "to": jid.JID(to),
                      "message": msg,
                      "subject": subject,
                      "type": mess_type
                    }
        
        if mess_data["type"] == "auto":
            # we try to guess the type 
            if mess_data["subject"]:
                mess_data["type"] = 'normal'
            elif not mess_data["to"].resource: #if to JID has a resource, the type is not 'groupchat'
                #we may have a groupchat message, we check if the we know this jid
                try:
                    entity_type = self.memory.getEntityData(mess_data["to"], ['type'], profile)["type"]
                    #FIXME: should entity_type manage ressources ?
                except (UnknownEntityError, KeyError):
                    entity_type = "contact"
                
                if entity_type == "chatroom":
                    mess_data["type"] = 'groupchat'
                else:
                    mess_data["type"] = 'chat'
            else:
                mess_data["type"] == 'chat'
            mess_data["type"] == "chat" if mess_data["subject"] else "normal"
        
        if not self.trigger.point("sendMessage", mess_data, profile):
            return
        
        debug(_("Sending jabber message of type [%(type)s] to %(to)s...") % {"type": mess_data["type"], "to": to})
        message = domish.Element((None,'message'))
        message["to"] = mess_data["to"].full()
        message["from"] = current_jid.full()
        message["type"] = mess_data["type"]
        if mess_data["subject"]:
            message.addElement("subject", None, subject)
        message.addElement("body", None, mess_data["message"])
        client.xmlstream.send(message)
        if mess_data["type"]!="groupchat":
            self.memory.addToHistory(current_jid, jid.JID(to), unicode(mess_data["message"]), unicode(mess_data["type"]), profile=profile) #we don't add groupchat message to history, as we get them back
                                                                                              #and they will be added then
            self.bridge.newMessage(message['from'], unicode(mess_data["message"]), mess_type=mess_data["type"], to_jid=message['to'], extra={}, profile=profile) #We send back the message, so all clients are aware of it


    def setPresence(self, to="", show="", priority = 0, statuses={}, profile_key='@DEFAULT@'):
        """Send our presence information"""
        profile = self.memory.getProfileName(profile_key)
        assert(profile)
        to_jid = jid.JID(to) if to else None
        self.profiles[profile].presence.available(to_jid, show, statuses, priority)
        #XXX: FIXME: temporary fix to work around openfire 3.7.0 bug (presence is not broadcasted to generating resource)
        if statuses.has_key(''):
            statuses['default'] = statuses['']
            del statuses['']
        self.bridge.presenceUpdate(self.profiles[profile].jid.full(),  show,
                int(priority), statuses, profile)
        
    
    def subscription(self, subs_type, raw_jid, profile_key):
        """Called to manage subscription
        @param subs_type: subsciption type (cf RFC 3921)
        @param raw_jid: unicode entity's jid
        @param profile_key: profile"""
        profile = self.memory.getProfileName(profile_key)
        assert(profile)
        to_jid = jid.JID(raw_jid)
        debug (_('subsciption request [%(subs_type)s] for %(jid)s') % {'subs_type':subs_type, 'jid':to_jid.full()})
        if subs_type=="subscribe":
            self.profiles[profile].presence.subscribe(to_jid)
        elif subs_type=="subscribed":
            self.profiles[profile].presence.subscribed(to_jid)
        elif subs_type=="unsubscribe":
            self.profiles[profile].presence.unsubscribe(to_jid)
        elif subs_type=="unsubscribed":
            self.profiles[profile].presence.unsubscribed(to_jid)

    def addContact(self, to, profile_key):
        """Add a contact in roster list"""
        profile = self.memory.getProfileName(profile_key)
        assert(profile)
        to_jid=jid.JID(to)
        #self.profiles[profile].roster.addItem(to_jid) XXX: disabled (cf http://wokkel.ik.nu/ticket/56))
        self.profiles[profile].presence.subscribe(to_jid)

    def updateContact(self, to, name, groups, profile_key):
        """update a contact in roster list"""
        profile = self.memory.getProfileName(profile_key)
        assert(profile)
        to_jid = jid.JID(to)
        groups = set(groups)
        roster_item = RosterItem(to_jid)
        roster_item.name = name or None
        roster_item.groups = set(groups)
        self.profiles[profile].roster.updateItem(roster_item)

    def delContact(self, to, profile_key):
        """Remove contact from roster list"""
        profile = self.memory.getProfileName(profile_key)
        assert(profile)
        to_jid=jid.JID(to)
        self.profiles[profile].roster.removeItem(to_jid)
        self.profiles[profile].presence.unsubscribe(to_jid)


    ## callbacks ##

    def serverDisco(self, disco, profile):
        """xep-0030 Discovery Protocol."""
        for feature in disco.features:
            debug (_("Feature found: %s"),feature)
            self.memory.addServerFeature(feature, profile)
        for cat, type in disco.identities:
            debug (_("Identity found: [%(category)s/%(type)s] %(identity)s") % {'category':cat, 'type':type, 'identity':disco.identities[(cat,type)]})

    def serverDiscoItems(self, disco_result, disco_client, profile, initialized):
        """xep-0030 Discovery Protocol.
        @param disco_result: result of the disco item querry
        @param disco_client: SatDiscoProtocol instance 
        @param profile: profile of the user 
        @param initialized: deferred which must be chained when everything is done"""
        
        def _check_entity_cb(result, entity, profile):
            for category, type in result.identities:
                debug (_('Identity added: (%(category)s,%(type)s) ==> %(entity)s [%(profile)s]') % {
                         'category':category, 'type':type, 'entity':entity, 'profile':profile})
                self.memory.addServerIdentity(category, type, entity, profile) 

        def _errback(result, entity, profile):
            warning(_("Can't get information on identity [%(entity)s] for profile [%(profile)s]") % {'entity':entity, 'profile': profile})
       
        defer_list = []
        for item in disco_result._items:
            if item.entity.full().count('.') == 1: #XXX: workaround for a bug on jabberfr, tmp
                warning(_('Using jabberfr workaround, be sure your domain has at least two levels (e.g. "example.tld", not "example" alone)'))
                continue
            args = [item.entity, profile] 
            defer_list.append(disco_client.requestInfo(item.entity).addCallbacks(_check_entity_cb, _errback, args, None, args))
        defer.DeferredList(defer_list).chainDeferred(initialized)

    
    ## Generic HMI ## 
    
    def actionResult(self, action_id, action_type, data, profile):
        """Send the result of an action
        @param action_id: same action_id used with action
        @param action_type: result action_type ("PARAM", "SUCCESS", "ERROR", "XMLUI")
        @param data: dictionary
        """
        self.bridge.actionResult(action_type, action_id, data, profile)

    def actionResultExt(self, action_id, action_type, data, profile):
        """Send the result of an action, extended version
        @param action_id: same action_id used with action
        @param action_type: result action_type /!\ only "DICT_DICT" for this method
        @param data: dictionary of dictionaries
        """
        if action_type != "DICT_DICT":
            error(_("action_type for actionResultExt must be DICT_DICT, fixing it"))
            action_type = "DICT_DICT"
        self.bridge.actionResultExt(action_type, action_id, data, profile)



    def askConfirmation(self, conf_id, conf_type, data, cb, profile):
        """Add a confirmation callback
        @param conf_id: conf_id used to get answer
        @param conf_type: confirmation conf_type ("YES/NO", "FILE_TRANSFER")
        @param data: data (depend of confirmation conf_type)
        @param cb: callback called with the answer
        """
        client = self.getClient(profile)
        if not client:
            raise ProfileUnknownError(_("Asking confirmation a non-existant profile"))
        if client._waiting_conf.has_key(conf_id):
            error (_("Attempt to register two callbacks for the same confirmation"))
        else:
            client._waiting_conf[conf_id] = (conf_type, data, cb)
            self.bridge.askConfirmation(conf_id, conf_type, data, profile)


    def confirmationAnswer(self, conf_id, accepted, data, profile):
        """Called by frontends to answer confirmation requests"""
        client = self.getClient(profile)
        if not client:
            raise ProfileUnknownError(_("Confirmation answer from a non-existant profile"))
        debug (_("Received confirmation answer for conf_id [%(conf_id)s]: %(success)s") % {'conf_id': conf_id, 'success':_("accepted") if accepted else _("refused")})
        if not client._waiting_conf.has_key(conf_id):
            error (_("Received an unknown confirmation (%(id)s for %(profile)s)") % {'id': conf_id, 'profile': profile})
        else:
            cb = client._waiting_conf[conf_id][-1]
            del client._waiting_conf[conf_id]
            cb(conf_id, accepted, data, profile)

    def registerProgressCB(self, progress_id, CB, profile):
        """Register a callback called when progress is requested for id"""
        client = self.getClient(profile)
        if not client:
            raise ProfileUnknownError
        client._progress_cb_map[progress_id] = CB

    def removeProgressCB(self, progress_id, profile):
        """Remove a progress callback"""
        client = self.getClient(profile)
        if not client:
            raise ProfileUnknownError
        if not client._progress_cb_map.has_key(progress_id):
            error (_("Trying to remove an unknow progress callback"))
        else:
            del client._progress_cb_map[progress_id]

    def getProgress(self, progress_id, profile):
        """Return a dict with progress information
        data['position'] : current possition
        data['size'] : end_position
        """
        client = self.getClient(profile)
        if not profile:
            raise ProfileNotInCacheError
        data = {}
        try:
            client._progress_cb_map[progress_id](progress_id, data, profile)
        except KeyError:
            pass
            #debug("Requested progress for unknown progress_id")
        return data

    def registerGeneralCB(self, name, CB):
        """Register a callback called for general reason"""
        self.__general_cb_map[name] = CB

    def removeGeneralCB(self, name):
        """Remove a general callback"""
        if not self.__general_cb_map.has_key(name):
            error (_("Trying to remove an unknow general callback"))
        else:
            del self.__general_cb_map[name]

    def callGeneralCB(self, name, *args, **kwargs):
        """Call general function back"""
        try:
            return self.__general_cb_map[name](*args, **kwargs)
        except KeyError:
            error(_("Trying to call unknown function (%s)") % name)
            return None

    #Menus management

    def importMenu(self, category, name, callback, help_string = "", type = "NORMAL"):
        """register a new menu for frontends
        @param category: category of the menu
        @param name: menu item entry
        @param callback: method to be called when menuitem is selected"""
        if self.menus.has_key((category,name)):
            error ("Want to register a menu which already existe")
            return
        self.menus[(category,name,type)] = {'callback':callback, 'help_string':help_string, 'type':type}

    def getMenus(self):
        """Return all menus registered"""
        return self.menus.keys()

    def getMenuHelp(self, category, name, type="NORMAL"):
        """return the help string of the menu"""
        try:
            return self.menus[(category,name,type)]['help_string']
        except KeyError:
            error (_("Trying to access an unknown menu"))
            return ""

    def callMenu(self, category, name, type="NORMAL", profile_key='@DEFAULT@'):
        """return the id of the action"""
        profile = self.memory.getProfileName(profile_key)
        if not profile_key:
            error (_('Non-exsitant profile'))
            return ""
        if self.menus.has_key((category,name,type)):
            id = self.get_next_id()
            self.menus[(category,name,type)]['callback'](id, profile)
            return id
        else:
            error (_("Trying to access an unknown menu (%(category)s/%(name)s/%(type)s)")%{'category':category, 'name':name,'type':type})
            return ""
