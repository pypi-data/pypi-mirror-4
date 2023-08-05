#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SAT plugin for managing xep-0045
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

from logging import debug, info, warning, error
from twisted.internet import defer
from twisted.words.protocols.jabber import jid

from sat.core import exceptions

import uuid

from wokkel import muc


try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

PLUGIN_INFO = {
"name": "XEP 0045 Plugin",
"import_name": "XEP-0045",
"type": "XEP",
"protocols": ["XEP-0045"],
"dependencies": [],
"main": "XEP_0045",
"handler": "yes",
"description": _("""Implementation of Multi-User Chat""")
}

class UnknownRoom(Exception):
    pass

class XEP_0045():

    def __init__(self, host):
        info(_("Plugin XEP_0045 initialization"))
        self.host = host
        self.clients={}
        host.bridge.addMethod("joinMUC", ".plugin", in_sign='ssa{ss}s', out_sign='', method=self._join)
        host.bridge.addMethod("mucNick", ".plugin", in_sign='sss', out_sign='', method=self.mucNick)
        host.bridge.addMethod("mucLeave", ".plugin", in_sign='ss', out_sign='', method=self.leave)
        host.bridge.addMethod("getRoomsJoined", ".plugin", in_sign='s', out_sign='a(sass)', method=self.getRoomsJoined)
        host.bridge.addMethod("getRoomsSubjects", ".plugin", in_sign='s', out_sign='a(ss)', method=self.getRoomsSubjects)
        host.bridge.addMethod("getUniqueRoomName", ".plugin", in_sign='s', out_sign='s', method=self.getUniqueName)
        host.bridge.addSignal("roomJoined", ".plugin", signature='sasss') #args: room_jid, room_nicks, user_nick, profile
        host.bridge.addSignal("roomLeft", ".plugin", signature='ss') #args: room_jid, profile
        host.bridge.addSignal("roomUserJoined", ".plugin", signature='ssa{ss}s') #args: room_jid, user_nick, user_data, profile
        host.bridge.addSignal("roomUserLeft", ".plugin", signature='ssa{ss}s') #args: room_jid, user_nick, user_data, profile
        host.bridge.addSignal("roomUserChangedNick", ".plugin", signature='ssss') #args: room_jid, old_nick, new_nick, profile
        host.bridge.addSignal("roomNewSubject", ".plugin", signature='sss') #args: room_jid, subject, profile


    def __check_profile(self, profile):
        """check if profile is used and connected
        if profile known but disconnected, remove it from known profiles
        @param profile: profile to check
        @return: True if the profile is known and connected, else False"""
        if not profile or not self.clients.has_key(profile) or not self.host.isConnected(profile):
            error (_('Unknown or disconnected profile (%s)') % profile)
            if self.clients.has_key(profile):
                del self.clients[profile]
            return False
        return True

    def __room_joined(self, room, profile):
        """Called when the user is in the requested room"""
        def _sendBridgeSignal(ignore=None):
            self.host.bridge.roomJoined(room.roomJID.userhost(), [user.nick for user in room.roster.values()], room.nick, profile)

        room_jid_s = room.roomJID.userhost()
        self.host.memory.updateEntityData(room.roomJID, "type", "chatroom", profile)
        self.clients[profile].joined_rooms[room_jid_s] = room
        if room.locked:
            #FIXME: the current behaviour is to create an instant room
            #and send the signal only when the room is unlocked
            #a proper configuration management should be done
            print "room locked !"
            self.clients[profile].configure(room.roomJID, {}).addCallbacks(_sendBridgeSignal, lambda x: error(_('Error while configuring the room')))
        else:
            _sendBridgeSignal()
        return room


    def __err_joining_room(self, failure, room_jid, nick, history_options, password, profile):
        """Called when something is going wrong when joining the room"""
        if failure.value.condition == 'conflict':
            # we have a nickname conflict, we try again with "_" suffixed to current nickname
            nick += '_'
            return self.clients[profile].join(room_jid, nick, history_options, password).addCallbacks(self.__room_joined, self.__err_joining_room, callbackKeywords={'profile':profile}, errbackArgs=[room_jid, nick, history_options, password, profile])
        
        mess = _("Error when joining the room")
        error (mess)
        self.host.bridge.newAlert(mess, _("Group chat error"), "ERROR", profile)
        raise failure

    def getRoomsJoined(self, profile_key='@DEFAULT@'):
        """Return room where user is"""
        profile = self.host.memory.getProfileName(profile_key)
        result = []
        if not self.__check_profile(profile):
            return result
        for room in self.clients[profile].joined_rooms.values():
            result.append((room.roomJID.userhost(), [user.nick for user in room.roster.values()], room.nick))
        return result

    def getRoomNick(self, room_jid_s, profile_key='@DEFAULT@'):
        """return nick used in room by user
        @param room_jid_s: unicode room id
        @profile_key: profile
        @return: nick or empty string in case of error"""
        profile = self.host.memory.getProfileName(profile_key)
        if not self.__check_profile(profile) or not self.clients[profile].joined_rooms.has_key(room_jid_s):
            return ''
        return self.clients[profile].joined_rooms[room_jid_s].nick
  
    def isNickInRoom(self, room_jid, nick, profile):
        """Tell if a nick is currently present in a room"""
        profile = self.host.memory.getProfileName(profile)
        if not self.__check_profile(profile):
            raise exceptions.UnknownProfileError("Unknown or disconnected profile")
        if not self.clients[profile].joined_rooms.has_key(room_jid.userhost()):
            raise UnknownRoom("This room has not been joined") 
        return self.clients[profile].joined_rooms[room_jid.userhost()].inRoster(nick)

    def getRoomsSubjects(self, profile_key='@DEFAULT@'):
        """Return received subjects of rooms"""
        profile = self.host.memory.getProfileName(profile_key)
        if not self.__check_profile(profile):
            return []
        return self.clients[profile].rec_subjects.values()

    def getUniqueName(self, profile_key='@DEFAULT@'):
        """Return unique name for room, avoiding collision"""
        #TODO: we should use #RFC-0045 10.1.4 when available here
        #TODO: we should be able to select the MUC service here
        return uuid.uuid1() 

    def join(self, room_jid, nick, options, profile_key='@DEFAULT@'):
        def _errDeferred(exc_obj = Exception, txt='Error while joining room'):
            d = defer.Deferred()
            d.errback(exc_obj(txt))
            return d

        profile = self.host.memory.getProfileName(profile_key)
        if not self.__check_profile(profile):
            return _errDeferred() 
        if self.clients[profile].joined_rooms.has_key(room_jid.userhost()):
            warning(_('%(profile)s is already in room %(room_jid)s') % {'profile':profile, 'room_jid':room_jid.userhost()})
            return _errDeferred() 
        info (_("[%(profile)s] is joining room %(room)s with nick %(nick)s") % {'profile':profile,'room':room_jid.userhost(), 'nick':nick})

        history_options = options["history"] == "True" if options.has_key("history") else None
        password = options["password"] if options.has_key("password") else None
        
        return self.clients[profile].join(room_jid, nick, history_options, password).addCallbacks(self.__room_joined, self.__err_joining_room, callbackKeywords={'profile':profile}, errbackArgs=[room_jid, nick, history_options, password, profile])

    def _join(self, room_jid_s, nick, options={}, profile_key='@DEFAULT@'):
        """join method used by bridge: use the _join method, but doesn't return any deferred"""
        profile = self.host.memory.getProfileName(profile_key)
        if not self.__check_profile(profile):
            return
        try:
            room_jid = jid.JID(room_jid_s)
        except:
            mess = _("Invalid room jid: %s") % room_jid_s
            warning(mess)
            self.host.bridge.newAlert(mess, _("Group chat error"), "ERROR", profile)
            return
        d = self.join(room_jid, nick, options, profile)
        d.addErrback(lambda x: warning(_('Error while joining room'))) #TODO: error management + signal in bridge

    def nick(self, room_jid, nick, profile_key):
        profile = self.host.memory.getProfileName(profile_key)
        if not self.__check_profile(profile):
            raise exceptions.UnknownProfileError("Unknown or disconnected profile")
        if not self.clients[profile].joined_rooms.has_key(room_jid.userhost()):
            raise UnknownRoom("This room has not been joined") 
        return self.clients[profile].nick(room_jid, nick)
  
    def leave(self, room_jid, profile_key): 
        profile = self.host.memory.getProfileName(profile_key)
        if not self.__check_profile(profile):
            raise exceptions.UnknownProfileError("Unknown or disconnected profile")
        if not self.clients[profile].joined_rooms.has_key(room_jid.userhost()):
            raise UnknownRoom("This room has not been joined") 
        return self.clients[profile].leave(room_jid)

    def subject(self, room_jid, subject, profile_key): 
        profile = self.host.memory.getProfileName(profile_key)
        if not self.__check_profile(profile):
            raise exceptions.UnknownProfileError("Unknown or disconnected profile")
        if not self.clients[profile].joined_rooms.has_key(room_jid.userhost()):
            raise UnknownRoom("This room has not been joined") 
        return self.clients[profile].subject(room_jid, subject)

    def mucNick(self, room_jid_s, nick, profile_key='@DEFAULT@'):
        """Change nickname in a room"""
        return self.nick(jid.JID(room_jid_s), nick, profile_key)

    def mucLeave(self, room_jid_s, profile_key='@DEFAULT@'):
        """Leave a room"""
        return self.leave(jid.JID(room_jid_s), profile_key)

    def getHandler(self, profile):
        self.clients[profile] = SatMUCClient(self)
        return self.clients[profile]


class SatMUCClient (muc.MUCClient):
    #implements(iwokkel.IDisco)
   
    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host
        muc.MUCClient.__init__(self)
        self.joined_rooms = {} #FIXME: seem to do the same thing as MUCClient's _rooms attribute, must be removed
        self.rec_subjects = {}
        self.__changing_nicks = set() # used to keep trace of who is changing nick,
                                      # and to discard userJoinedRoom signal in this case
        print "init SatMUCClient OK"

    def subject(self, room, subject):
        return muc.MUCClientProtocol.subject(self, room, subject)
    
    def unavailableReceived(self, presence):
        #XXX: we override this method to manage nickname change
        #TODO: feed this back to Wokkel
        """
        Unavailable presence was received.

        If this was received from a MUC room occupant JID, that occupant has
        left the room.
        """
        room, user = self._getRoomUser(presence)

        if room is None or user is None:
            return

        room.removeUser(user)

        if muc.STATUS_CODE.NEW_NICK in presence.mucStatuses:
            self.__changing_nicks.add(presence.nick)
            self.userChangedNick(room, user, presence.nick)
        else:
            self.__changing_nicks.discard(presence.nick)
            self.userLeftRoom(room, user)

    def receivedGroupChat(self, room, user, body):
        debug('receivedGroupChat: room=%s user=%s body=%s', room, user, body)

    def userJoinedRoom(self, room, user):
        if user.nick in self.__changing_nicks:
            self.__changing_nicks.remove(user.nick)
        else:
            debug (_("user %(nick)s has joined room (%(room_id)s)") % {'nick':user.nick, 'room_id':room.occupantJID.userhost()})
            if not self.host.trigger.point("MUC user joined", room, user, self.parent.profile):
                return
            user_data={'entity':user.entity.full() if user.entity else  '', 'affiliation':user.affiliation, 'role':user.role} 
            self.host.bridge.roomUserJoined(room.roomJID.userhost(), user.nick, user_data, self.parent.profile)
    
    def userLeftRoom(self, room, user):
        if user.nick == room.nick:
            # we left the room
            room_jid_s = room.roomJID.userhost()
            info (_("Room [%(room)s] left (%(profile)s))") % { "room": room_jid_s,
                                                               "profile": self.parent.profile })
            self.host.memory.delEntityCache(room.roomJID, self.parent.profile)
            del self.plugin_parent.clients[self.parent.profile].joined_rooms[room_jid_s]
            self.host.bridge.roomLeft(room.roomJID.userhost(), self.parent.profile)
        else:
            debug (_("user %(nick)s left room (%(room_id)s)") % {'nick':user.nick, 'room_id':room.occupantJID.userhost()})
            user_data={'entity':user.entity.full() if user.entity else  '', 'affiliation':user.affiliation, 'role':user.role} 
            self.host.bridge.roomUserLeft(room.roomJID.userhost(), user.nick, user_data, self.parent.profile)

    def userChangedNick(self, room, user, new_nick):
            self.host.bridge.roomUserChangedNick(room.roomJID.userhost(), user.nick, new_nick, self.parent.profile)

    def userUpdatedStatus(self, room, user, show, status):
        print("FIXME: MUC status not managed yet")
        #FIXME:

    def receivedSubject(self, room, user, subject):
        debug (_("New subject for room (%(room_id)s): %(subject)s") % {'room_id':room.roomJID.full(),'subject':subject})
        self.rec_subjects[room.roomJID.userhost()] = (room.roomJID.userhost(), subject)
        self.host.bridge.roomNewSubject(room.roomJID.userhost(), subject, self.parent.profile)

    #def connectionInitialized(self):
        #pass
    
    #def getDiscoInfo(self, requestor, target, nodeIdentifier=''):
        #return [disco.DiscoFeature(NS_VCARD)]

    #def getDiscoItems(self, requestor, target, nodeIdentifier=''):
        #return []
    
