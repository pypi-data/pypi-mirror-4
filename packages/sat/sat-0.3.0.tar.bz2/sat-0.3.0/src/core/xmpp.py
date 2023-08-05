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

from twisted.internet import task, defer
from twisted.words.protocols.jabber import jid, xmlstream
from wokkel import client, disco, xmppim, generic, compat, delay
from logging import debug, info, error
from sat.core import exceptions
from calendar import timegm


class SatXMPPClient(client.XMPPClient):
    
    def __init__(self, host_app, profile, user_jid, password, host=None, port=5222):
        client.XMPPClient.__init__(self, user_jid, password, host, port)
        self.factory.clientConnectionLost = self.connectionLost
        self.__connected=False
        self.profile = profile
        self.host_app = host_app
        self.client_initialized = defer.Deferred()
        self.conn_deferred = defer.Deferred()
        self._waiting_conf = {}  #callback called when a confirmation is received
        self._progress_cb_map = {}  #callback called when a progress is requested (key = progress id)
        

    def getConnectionDeferred(self):
        """Return a deferred which fire when the client is connected"""
        return self.conn_deferred

    def _authd(self, xmlstream):
        if not self.host_app.trigger.point("XML Initialized", xmlstream, self.profile):
            return
        client.XMPPClient._authd(self, xmlstream)
        self.__connected=True
        info (_("********** [%s] CONNECTED **********") % self.profile)
        self.streamInitialized()
        self.host_app.bridge.connected(self.profile) #we send the signal to the clients
   

    def streamInitialized(self):
        """Called after _authd"""
        debug (_("XML stream is initialized"))
        self.keep_alife = task.LoopingCall(self.xmlstream.send, " ")  #Needed to avoid disconnection (specially with openfire)
        self.keep_alife.start(180)
        
        self.disco = SatDiscoProtocol(self)
        self.disco.setHandlerParent(self)
        self.discoHandler = disco.DiscoHandler()
        self.discoHandler.setHandlerParent(self)
        
        if not self.host_app.trigger.point("Disco Handled", self.profile):
            return

        self.roster.requestRoster()
        
        self.presence.available()
       
        self.disco.requestInfo(jid.JID(self.jid.host)).addCallback(self.host_app.serverDisco, self.profile)  #FIXME: use these informations
        
        self.disco.requestItems(jid.JID(self.jid.host)).addCallback(self.host_app.serverDiscoItems, self.disco, self.profile, self.client_initialized)
        self.conn_deferred.callback(None)

    def initializationFailed(self, reason):
        print ("initializationFailed: %s" % reason)
        self.host_app.bridge.connectionError("AUTH_ERROR", self.profile)
        try:
            client.XMPPClient.initializationFailed(self, reason)
        except:
            #we already send an error signal, no need to raise an exception
            pass
        self.conn_deferred.errback()

    def isConnected(self):
        return self.__connected
    
    def connectionLost(self, connector, unused_reason):
        self.__connected=False
        info (_("********** [%s] DISCONNECTED **********") % self.profile)
        try:
            self.keep_alife.stop()
        except AttributeError:
            debug (_("No keep_alife"))
        self.host_app.bridge.disconnected(self.profile) #we send the signal to the clients
        self.host_app.purgeClient(self.profile) #and we remove references to this client


class SatMessageProtocol(xmppim.MessageProtocol):
    
    def __init__(self, host):
        xmppim.MessageProtocol.__init__(self)
        self.host = host

    def onMessage(self, message):
        debug (_(u"got message from: %s"), message["from"])
        if not self.host.trigger.point("MessageReceived", message, profile=self.parent.profile):
            return
        for e in message.elements():
            if e.name == "body":
                mess_type = message['type'] if message.hasAttribute('type') else 'normal'
                mess_body = e.children[0] if e.children else ""
                try:
                    _delay = delay.Delay.fromElement(filter(lambda elm: elm.name == 'delay', message.elements())[0])
                    timestamp = timegm(_delay.stamp.utctimetuple())
                    extra = {"archive": str(timestamp)}
                    if mess_type != 'groupchat': #XXX: we don't save delayed messages in history for groupchats
                        #TODO: add delayed messages to history if they aren't already in it
                        self.host.memory.addToHistory(jid.JID(message["from"]), jid.JID(message["to"]), mess_body, mess_type, timestamp, profile=self.parent.profile)
                except IndexError:
                    extra = {}
                    self.host.memory.addToHistory(jid.JID(message["from"]), jid.JID(message["to"]), mess_body, mess_type, profile=self.parent.profile)
                self.host.bridge.newMessage(message["from"], mess_body, mess_type, message['to'], extra, profile=self.parent.profile)
                break
    
class SatRosterProtocol(xmppim.RosterClientProtocol):

    def __init__(self, host):
        xmppim.RosterClientProtocol.__init__(self)
        self.host = host
        self.got_roster = defer.Deferred()
        #XXX: the two following dicts keep a local copy of the roster
        self._groups = {} #map from groups to bare jids: key=group value=set of bare jids
        self._jids = {} #map from bare jids to RosterItem: key=jid value=RosterItem
    
    def rosterCb(self, roster):
        for raw_jid, item in roster.iteritems():
            self.onRosterSet(item)

    def requestRoster(self):
        """ ask the server for Roster list """
        debug("requestRoster")
        d = self.getRoster().addCallback(self.rosterCb)
        d.chainDeferred(self.got_roster)

    def removeItem(self, to):
        """Remove a contact from roster list"""
        xmppim.RosterClientProtocol.removeItem(self, to)
        #TODO: check IQ result
    
    #XXX: disabled (cf http://wokkel.ik.nu/ticket/56))
    #def addItem(self, to):
        #"""Add a contact to roster list"""
        #xmppim.RosterClientProtocol.addItem(self, to)
        #TODO: check IQ result"""

    def updateItem(self, roster_item):
        """
        Update an item of the contact list.

        @param roster_item: item to update
        """
        iq = compat.IQ(self.xmlstream, 'set')
        iq.addElement((xmppim.NS_ROSTER, 'query'))
        item = iq.query.addElement('item')
        item['jid'] = roster_item.jid.userhost()
        if roster_item.name:
            item['name'] = roster_item.name
        for group in roster_item.groups:
            item.addElement('group', content=group)
        return iq.send()

    def getAttributes(self, item):
        """Return dictionary of attributes as used in bridge from a RosterItem
        @param item: RosterItem
        @return: dictionary of attributes"""
        item_attr = {'to': unicode(item.subscriptionTo),
                     'from': unicode(item.subscriptionFrom),
                     'ask': unicode(item.ask)
                     }
        if item.name:
            item_attr['name'] = item.name
        return item_attr
    
    def onRosterSet(self, item):
        """Called when a new/update roster item is received"""
        #TODO: send a signal to frontends
        if not item.subscriptionTo and not item.subscriptionFrom and not item.ask:
            #XXX: current behaviour: we don't want contact in our roster list
            #if there is no presence subscription
            #may change in the future
            self.removeItem(item.jid)
            return
        info (_("new contact in roster list: %s"), item.jid.full())
        #self.host.memory.addContact(item.jid, item_attr, item.groups, self.parent.profile)
       
        bare_jid = item.jid.userhost()
        self._jids[bare_jid] = item
        for group in item.groups:
            self._groups.setdefault(group,set()).add(bare_jid)
        self.host.bridge.newContact(item.jid.full(), self.getAttributes(item), item.groups, self.parent.profile)
    
    def onRosterRemove(self, entity):
        """Called when a roster removal event is received"""
        print _("removing %s from roster list") % entity.full()
        bare_jid = entity.userhost()

        #we first remove item from local cache (self._groups and self._jids)
        try:
            item = self._jids.pop(bare_jid)
        except KeyError:
            log.warning("Received a roster remove event for an item not in cache")
            return
        for group in item.groups:
            try:
                jids_set = self._groups[group]
                jids_set.remove(bare_jid)
                if not jids_set:
                    del self._groups[group]
            except KeyError:
                log.warning("there is not cache for the group [%(groups)s] of the removed roster item [%(jid)s]" %
                            {"group": group, "jid": bare_jid})
                                                                                                                            
        #then we send the bridge signal
        self.host.bridge.contactDeleted(entity.userhost(), self.parent.profile)

    def getGroups(self):
        """Return a list of groups"""
        return self._groups.keys()

    def getItem(self, jid):
        """Return RosterItem for a given jid
        @param jid: jid of the contact
        @return: RosterItem or None if contact is not in cache"""
        return self._jids.get(jid.userhost(), None)

    def getBareJids(self):
        """Return all bare jids (as unicode) of the roster"""
        return self._jids.keys()

    def isJidInRoster(self, entity_jid):
        """Return True if jid is in roster"""
        return entity_jid.userhost() in self._jids
    
    def getItems(self):
        """Return all items of the roster"""
        return self._jids.values()

    def getJidsFromGroup(self, group):
        try:
            return self._groups[group]
        except KeyError:
            return  exceptions.UnknownGroupError
        

class SatPresenceProtocol(xmppim.PresenceClientProtocol):

    def __init__(self, host):
        xmppim.PresenceClientProtocol.__init__(self)
        self.host = host
    
    def availableReceived(self, entity, show=None, statuses=None, priority=0):
        debug (_("presence update for [%(entity)s] (available, show=%(show)s statuses=%(statuses)s priority=%(priority)d)") % {'entity':entity, 'show':show, 'statuses':statuses, 'priority':priority})
        
        if not statuses:
            statuses = {}
        
        if statuses.has_key(None):   #we only want string keys
            statuses["default"] = statuses[None]
            del statuses[None]

        self.host.memory.setPresenceStatus(entity, show or "",
                int(priority), statuses, self.parent.profile)

        #now it's time to notify frontends
        self.host.bridge.presenceUpdate(entity.full(),  show or "",
                int(priority), statuses, self.parent.profile)
    
    def unavailableReceived(self, entity, statuses=None):
        debug (_("presence update for [%(entity)s] (unavailable, statuses=%(statuses)s)") % {'entity':entity, 'statuses':statuses})
        
        if not statuses:
            statuses = {}
        
        if statuses.has_key(None):   #we only want string keys
            statuses["default"] = statuses[None]
            del statuses[None]
        self.host.memory.setPresenceStatus(entity, "unavailable", 0, statuses, self.parent.profile)

        #now it's time to notify frontends
        self.host.bridge.presenceUpdate(entity.full(), "unavailable", 0, statuses, self.parent.profile)
        
    
    def available(self, entity=None, show=None, statuses=None, priority=0):
        if not statuses:
            statuses = {}
            # default for us is None for wokkel
            # so we must temporarily switch to wokkel's convention...	
            if 'default' in statuses:
                statuses[None] = statuses['default']

            xmppim.PresenceClientProtocol.available(self, entity, show, statuses, priority)
            presence_elt = xmppim.AvailablePresence(entity, show, statuses, priority)
            if not self.host.trigger.point("presence_available", presence_elt, self.parent):
                return
            self.send(presence_elt)

        # ... before switching back
        if None in statuses:
            del statuses[None]

    def subscribed(self, entity):
        xmppim.PresenceClientProtocol.subscribed(self, entity)
        self.host.memory.delWaitingSub(entity.userhost(), self.parent.profile)
        item = self.parent.roster.getItem(entity)
        if not item or not item.subscriptionTo: #we automatically subscribe to 'to' presence
            debug(_('sending automatic "from" subscription request'))
            self.subscribe(entity)

    def unsubscribed(self, entity):
        xmppim.PresenceClientProtocol.unsubscribed(self, entity)
        self.host.memory.delWaitingSub(entity.userhost(), self.parent.profile)

    def subscribedReceived(self, entity):
        debug (_("subscription approved for [%s]") % entity.userhost())
        self.host.bridge.subscribe('subscribed', entity.userhost(), self.parent.profile)

    def unsubscribedReceived(self, entity):
        debug (_("unsubscription confirmed for [%s]") % entity.userhost())
        self.host.bridge.subscribe('unsubscribed', entity.userhost(), self.parent.profile)

    def subscribeReceived(self, entity):
        debug (_("subscription request from [%s]") % entity.userhost())
        item = self.parent.roster.getItem(entity)
        if item and item.subscriptionTo:
            #We automatically accept subscription if we are already subscribed to contact presence
            debug(_('sending automatic subscription acceptance'))
            self.subscribed(entity)
        else:
            self.host.memory.addWaitingSub('subscribe', entity.userhost(), self.parent.profile)
            self.host.bridge.subscribe('subscribe', entity.userhost(), self.parent.profile)

    def unsubscribeReceived(self, entity):
        debug (_("unsubscription asked for [%s]") % entity.userhost())
        item = self.parent.roster.getItem(entity)
        if item and item.subscriptionFrom: #we automatically remove contact
            debug(_('automatic contact deletion'))
            self.host.delContact(entity.userhost(), self.parent.profile)
        self.host.bridge.subscribe('unsubscribe', entity.userhost(), self.parent.profile)

class SatDiscoProtocol(disco.DiscoClientProtocol):
    def __init__(self, host):
        disco.DiscoClientProtocol.__init__(self)

class SatFallbackHandler(generic.FallbackHandler):
    def __init__(self, host):
        generic.FallbackHandler.__init__(self)

    def iqFallback(self, iq):
        if iq.handled == True:
            return
        debug (u"iqFallback: xml = [%s]" % (iq.toXml()))
        generic.FallbackHandler.iqFallback(self, iq)

class RegisteringAuthenticator(xmlstream.ConnectAuthenticator):

    def __init__(self, host, jabber_host, user_login, user_pass, email, answer_id, profile):
        xmlstream.ConnectAuthenticator.__init__(self, jabber_host)
        self.host = host
        self.jabber_host = jabber_host
        self.user_login = user_login
        self.user_pass = user_pass
        self.user_email = email
        self.answer_id = answer_id
        self.profile = profile
        print _("Registration asked for"),user_login, user_pass, jabber_host
    
    def connectionMade(self):
        print "connectionMade"
        
        self.xmlstream.namespace = "jabber:client"
        self.xmlstream.sendHeader()

        iq = compat.IQ(self.xmlstream, 'set')
        iq["to"] = self.jabber_host
        query = iq.addElement(('jabber:iq:register', 'query'))
        _user = query.addElement('username')
        _user.addContent(self.user_login)
        _pass = query.addElement('password')
        _pass.addContent(self.user_pass)
        if self.user_email:
            _email = query.addElement('email')
            _email.addContent(self.user_email)
        reg = iq.send(self.jabber_host).addCallbacks(self.registrationAnswer, self.registrationFailure)

    def registrationAnswer(self, answer):
        debug (_("registration answer: %s") % answer.toXml())
        answer_type = "SUCCESS"
        answer_data={"message":_("Registration successfull")}
        self.host.bridge.actionResult(answer_type, self.answer_id, answer_data, self.profile)
        self.xmlstream.sendFooter()
        
    def registrationFailure(self, failure):
        info (_("Registration failure: %s") % str(failure.value))
        answer_type = "ERROR"
        answer_data = {}
        if failure.value.condition == 'conflict':
            answer_data['reason'] = 'conflict'
            answer_data={"message":_("Username already exists, please choose an other one")}
        else:
            answer_data['reason'] = 'unknown'
            answer_data={"message":_("Registration failed (%s)") % str(failure.value.condition)}
        self.host.bridge.actionResult(answer_type, self.answer_id, answer_data, self.profile)
        self.xmlstream.sendFooter()

class SatVersionHandler(generic.VersionHandler):

    def getDiscoInfo(self, requestor, target, node):
        #XXX: We need to work around wokkel's behaviour (namespace not added if there is a
        # node) as it cause issues with XEP-0115 & PEP (XEP-0163): there is a node when server
        # ask for disco info, and not when we generate the key, so the hash is used with different
        # disco features, and when the server (seen on ejabberd) generate its own hash for security check
        # it reject our features (resulting in e.g. no notification on PEP)
        return generic.VersionHandler.getDiscoInfo(self, requestor, target, None)

