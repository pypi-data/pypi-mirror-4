#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SàT plugin for managing text commands
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

from twisted.words.protocols.jabber import jid
from logging import debug, info, warning, error

PLUGIN_INFO = {
"name": "Text commands",
"import_name": "text-commands",
"type": "Misc",
"protocols": [],
"dependencies": ["XEP-0045", "EXP-PARROT"],
"main": "TextCommands",
"handler": "no",
"description": _("""IRC like text commands""")
}

class TextCommands():
    #FIXME: doc strings for commands have to be translatable
    #       plugins need a dynamic translation system (translation
    #       should be downloadable independently)

    def __init__(self, host):
        info(_("Text commands initialization"))
        self.host = host
        host.trigger.add("sendMessage", self.sendMessageTrigger)

    def sendMessageTrigger(self, mess_data, profile):
        """ Check text commands in message, and react consequently """
        msg = mess_data["message"]
        if msg:
            if msg[0] == '/':
                command = msg[1:].partition(' ')[0].lower()
                if command.isalpha():
                    # looks like an actual command, we try to call the corresponding method
                    try:
                        mess_data["unparsed"] = msg[1+len(command):] #part not yet parsed of the message
                        return getattr(self,"cmd_%s" % command)(mess_data,profile)
                    except AttributeError:
                        pass
            elif msg[0] == '\\': #we have escape char
                try:
                    if msg[1] in ('/','\\'): # we have '\/' or '\\', we escape to '/' or '\'
                        mess_data["message"] = msg[1:]
                except IndexError:
                    pass
        return True

    def _getRoomJID(self, arg, service_jid):
        """Return a room jid with a shortcut
        @param arg: argument: can be a full room jid (e.g.: sat@chat.jabberfr.org)
                    or a shortcut (e.g.: sat or sat@ for sat on current service)
        @param service_jid: jid of the current service (e.g.: chat.jabberfr.org)
        """
        nb_arobas = arg.count('@')
        if nb_arobas == 1:
            if arg[-1] !='@':
                return jid.JID(arg)
            return jid.JID(arg+service_jid)
        return jid.JID(u"%s@%s" % (arg, service_jid))

    def _feedBack(self, message, mess_data, profile):
        """Give a message back to the user"""
        if mess_data["type"] == 'groupchat':
            _from = mess_data["to"].userhostJID()
        else:
            _from = self.host.getJidNStream(profile)[0]

        self.host.bridge.newMessage(unicode(mess_data["to"]), message, mess_data['type'], unicode(_from), {}, profile=profile)

    def cmd_nick(self, mess_data, profile):
        """change nickname"""
        debug("Catched nick command")
        
        if mess_data['type'] != "groupchat":
            #/nick command does nothing if we are not on a group chat
            info("Ignoring /nick command on a non groupchat message")
            
            return True
         
        nick = mess_data["unparsed"].strip()
        room = mess_data["to"]

        self.host.plugins["XEP-0045"].nick(room,nick,profile)

        return False
    
    def cmd_join(self, mess_data, profile):
        """join a new room (on the same service if full jid is not specified)"""
        debug("Catched join command")
        
        if mess_data['type'] != "groupchat":
            #/leave command does nothing if we are not on a group chat
            info("Ignoring /join command on a non groupchat message")
            return True
         
        if mess_data["unparsed"].strip():
            room = self._getRoomJID(mess_data["unparsed"].strip(), mess_data["to"].host)
            nick = (self.host.plugins["XEP-0045"].getRoomNick(mess_data["to"].userhost(), profile) or
                    self.host.getClient(profile).jid.user)
            self.host.plugins["XEP-0045"].join(room, nick, {}, profile)

        return False

    def cmd_leave(self, mess_data, profile):
        """quit a room"""
        debug("Catched leave command")
        
        if mess_data['type'] != "groupchat":
            #/leave command does nothing if we are not on a group chat
            info("Ignoring /leave command on a non groupchat message")
            return True
         
        if mess_data["unparsed"].strip():
            room = self._getRoomJID(mess_data["unparsed"].strip(), mess_data["to"].host) 
        else:
            room = mess_data["to"]

        self.host.plugins["XEP-0045"].leave(room,profile)

        return False

    def cmd_part(self, mess_data, profile):
        """just a synonym of /leave"""
        return self.cmd_leave(mess_data, profile)

    def cmd_title(self, mess_data, profile):
        """change room's subject"""
        debug("Catched title command")
        
        if mess_data['type'] != "groupchat":
            #/leave command does nothing if we are not on a group chat
            info("Ignoring /title command on a non groupchat message")
            return True
         
        subject = mess_data["unparsed"].strip()
        
        if subject:
            room = mess_data["to"]
            self.host.plugins["XEP-0045"].subject(room, subject, profile)

        return False

    def cmd_topic(self, mess_data, profile):
        """just a synonym of /title"""
        return self.cmd_title(mess_data, profile)

    def cmd_parrot(self, mess_data, profile):
        """activate Parrot mode between 2 entities, in both directions."""
        #TODO: these commands must not be hardcoded, an interface should be made
        #      to allow plugins to register simple commands like this.
        
        debug("Catched parrot command")
       
        try:
            link_left_jid = jid.JID(mess_data["unparsed"].strip())
            if not link_left_jid.user or not link_left_jid.host:
                raise jid.InvalidFormat
        except jid.InvalidFormat:
            self._feedBack("Can't activate Parrot mode for invalid jid", mess_data, profile)
            return False

        link_right_jid = mess_data['to']

        self.host.plugins["EXP-PARROT"].addParrot(link_left_jid, link_right_jid, profile)
        self.host.plugins["EXP-PARROT"].addParrot(link_right_jid, link_left_jid, profile)

        self._feedBack("Parrot mode activated for %s" % (unicode(link_left_jid),), mess_data, profile)
        
        return False

    def cmd_unparrot(self, mess_data, profile):
        """remove Parrot mode between 2 entities, in both directions."""
        debug("Catched unparrot command")
       
        try:
            link_left_jid = jid.JID(mess_data["unparsed"].strip())
            if not link_left_jid.user or not link_left_jid.host:
                raise jid.InvalidFormat
        except jid.InvalidFormat:
            self._feedBack("Can't deactivate Parrot mode for invalid jid", mess_data, profile)
            return False

        link_right_jid = mess_data['to']

        self.host.plugins["EXP-PARROT"].removeParrot(link_left_jid, profile)
        self.host.plugins["EXP-PARROT"].removeParrot(link_right_jid, profile)

        self._feedBack("Parrot mode deactivated for %s and %s" % (unicode(link_left_jid), unicode(link_right_jid)), mess_data, profile)
        
        return False

    def cmd_help(self, mess_data, profile):
        """show help on available commands"""
        commands=filter(lambda method: method.startswith('cmd_'), dir(self))
        longuest = max([len(command) for command in commands])
        help_cmds = []
        
        for command in commands:
            method = getattr(self, command)
            try:
                help_str = method.__doc__.split('\n')[0]
            except AttributeError:
                help_str = ''
            spaces = (longuest - len(command)) * ' '
            help_cmds.append("    /%s: %s %s" % (command[4:], spaces, help_str))

        help_mess = _(u"Text commands available:\n%s") % (u'\n'.join(help_cmds),) 
        self._feedBack(help_mess, mess_data, profile)
        

