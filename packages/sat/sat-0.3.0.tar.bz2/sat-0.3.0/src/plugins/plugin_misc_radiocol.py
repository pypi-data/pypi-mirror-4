#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SAT plugin for managing Radiocol 
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
from twisted.words.xish import domish
from twisted.internet import reactor
from twisted.words.protocols.jabber import jid

from wokkel import disco, iwokkel

from zope.interface import implements

import os.path
from os import unlink
from mutagen.oggvorbis import OggVorbis, OggVorbisHeaderError

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

MESSAGE = '/message'
NC_RADIOCOL = 'http://www.goffi.org/protocol/radiocol'
RADIOC_TAG = 'radiocol'
RADIOC_REQUEST = MESSAGE + '/' + RADIOC_TAG + '[@xmlns="' + NC_RADIOCOL + '"]'

PLUGIN_INFO = {
"name": "Radio collective plugin",
"import_name": "Radiocol",
"type": "Exp",
"protocols": [],
"dependencies": ["XEP-0045", "XEP-0249"],
"main": "Radiocol",
"handler": "yes",
"description": _("""Implementation of radio collective""")
}

QUEUE_LIMIT = 2


class Radiocol():

    def __init__(self, host):
        info(_("Radio collective initialization"))
        self.host = host
        self.radios={}
        host.bridge.addMethod("radiocolLaunch", ".plugin", in_sign='ass', out_sign='', method=self.radiocolLaunch)
        host.bridge.addMethod("radiocolCreate", ".plugin", in_sign='ss', out_sign='', method=self.radiocolCreate)
        host.bridge.addMethod("radiocolSongAdded", ".plugin", in_sign='sss', out_sign='', method=self.radiocolSongAdded)
        host.bridge.addSignal("radiocolStarted", ".plugin", signature='sss') #room_jid, referee, profile
        host.bridge.addSignal("radiocolSongRejected", ".plugin", signature='sss') #room_jid, reason, profile
        host.bridge.addSignal("radiocolPreload", ".plugin", signature='ssssss') #room_jid, filename, title, artist, album, profile
        host.bridge.addSignal("radiocolPlay", ".plugin", signature='sss') #room_jid, filename, profile
        host.bridge.addSignal("radiocolNoUpload", ".plugin", signature='ss') #room_jid, profile
        host.bridge.addSignal("radiocolUploadOk", ".plugin", signature='ss') #room_jid, profile
        host.trigger.add("MUC user joined", self.userJoinedTrigger)

    def createRadiocolElt(self, to_jid, type="normal"):
        type = "normal" if to_jid.resource else "groupchat"
        elt = domish.Element((None,'message'))
        elt["to"] = to_jid.full()
        elt["type"] = type
        elt.addElement((NC_RADIOCOL, RADIOC_TAG))
        return elt
    
    def __create_started_elt(self):
        """Create a game_started domish element"""
        started_elt = domish.Element((None,'started'))
        return started_elt

    def __create_preload_elt(self, sender, filename, title, artist, album):
        preload_elt = domish.Element((None,'preload'))
        preload_elt['sender'] = sender
        preload_elt['filename'] = filename #XXX: the frontend should know the temporary directory where file is put
        preload_elt['title'] = title
        preload_elt['artist'] = artist
        preload_elt['album'] = album
        return preload_elt


    def userJoinedTrigger(self, room, user, profile):
        """This trigger is used to check if we are waiting people in this room,
        and to create a game if everybody is here"""
        room_jid = room.occupantJID.userhost()
        if self.radios.has_key(room_jid) and self.radios[room_jid]["referee"] == room.occupantJID.full():
            #we are in a radiocol room, let's start the party !
            mess = self.createRadiocolElt(jid.JID(room_jid+'/'+user.nick))
            mess.firstChildElement().addChild(self.__create_started_elt())
            self.host.profiles[profile].xmlstream.send(mess)
        return True

    def radiocolLaunch(self, occupants, profile_key='@DEFAULT@'):
        """Launch a game: helper method to create a room, invite occupants, and create the radiocol
        @param occupants: list for occupants jid"""
        debug(_('Launching radiocol'))
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            error(_("Unknown profile"))
            return

        def radiocolRoomJoined(room):
            print "radiocolRoomJoined"
            _room_jid = room.occupantJID.userhostJID()
            self.radiocolCreate(_room_jid.userhost(), profile_key=profile)
            for occupant in occupants:
                self.host.plugins["XEP-0249"].invite(jid.JID(occupant), room.occupantJID.userhostJID(), {"game":"Radiocol"}, profile)
        
        def after_init(ignore):
            room_name = "sat_radiocol_%s" % self.host.plugins["XEP-0045"].getUniqueName(profile_key)
            print "\n\n===> room_name:", room_name
            muc_service = None
            for service in self.host.memory.getServerServiceEntities("conference", "text", profile):
                if not ".irc." in service.userhost():
                    #FIXME: 
                    #This awfull ugly hack is here to avoid an issue with openfire: the irc gateway
                    #use "conference/text" identity (instead of "conference/irc"), there is certainly a better way
                    #to manage this, but this hack fill do it for test purpose
                    muc_service = service
                    break
            if not muc_service:
                error(_("Can't find a MUC service"))
                return
            
            _jid, xmlstream = self.host.getJidNStream(profile)
            d = self.host.plugins["XEP-0045"].join(jid.JID("%s@%s" % (room_name, muc_service.userhost())), _jid.user, {}, profile)
            d.addCallback(radiocolRoomJoined)

        client = self.host.getClient(profile)
        if not client:
            error(_('No client for this profile key: %s') % profile_key)
            return
        client.client_initialized.addCallback(after_init)

    def radiocolCreate(self, room_jid_param, profile_key='@DEFAULT@'):
        """Create a new game
        @param room_jid_param: jid of the room
        @param profile_key: %(doc_profile_key)s"""
        debug (_("Creating Radiocol"))
        room_jid = jid.JID(room_jid_param)
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            error (_("profile %s is unknown") % profile_key)
            return
        if self.radios.has_key(room_jid):
            warning (_("Radiocol already started in room %s") % room_jid.userhost())
        else:
            room_nick = self.host.plugins["XEP-0045"].getRoomNick(room_jid.userhost(), profile)
            if not room_nick:
                error ('Internal error')
                return
            referee = room_jid.userhost() + '/' + room_nick
            self.radios[room_jid.userhost()] = {'referee':referee, 'queue':[], 'upload':True, 'playing': False, 'occupants_data':{}, 'to_delete':{}}
            mess = self.createRadiocolElt(jid.JID(room_jid.userhost()))
            mess.firstChildElement().addChild(self.__create_started_elt())
            self.host.profiles[profile].xmlstream.send(mess)

    def radiocolSongAdded(self, referee, song_path, profile):
        """This method is called by libervia when a song has been uploaded
        @param room_jid_param: jid of the room
        @song_path: absolute path of the song added
        @param profile_key: %(doc_profile_key)s"""
        #XXX: this is a Q&D way for the proof of concept. In the future, the song should
        #     be streamed to the backend using XMPP file copy
        #     Here we cheat because we know we are on the same host, and we don't
        #     check data. Referee will have to parse the song himself to check it
        client = self.host.getClient(profile)
        if not client:
            error(_("Can't access profile's data"))
            return 
        try:
            song = OggVorbis(song_path)
        except OggVorbisHeaderError:
            #this file is not ogg vorbis, we reject it
            unlink(song_path) # FIXME: same host trick (see note above)
            self.host.bridge.radiocolSongRejected(jid.JID(referee).userhost(), \
                                                  "Uploaded file is not Ogg Vorbis song, only Ogg Vorbis songs are acceptable", profile)
            """mess = self.createRadiocolElt(jid.JID(referee))
            reject_elt = mess.firstChildElement().addElement(('','song_rejected'))
            reject_elt['sender'] = client.jid
            reject_elt['reason'] = "Uploaded file is not Ogg Vorbis song, only Ogg Vorbis songs are acceptable"
            #FIXME: add an error code
            self.host.profiles[profile].xmlstream.send(mess)"""
            return
        title = song.get("title", ["Unknown"])[0]
        artist = song.get("artist", ["Unknown"])[0]
        album = song.get("album", ["Unknown"])[0]
        length = song.info.length
        mess = self.createRadiocolElt(jid.JID(referee))
        added_elt = mess.firstChildElement().addElement(('','song_added'))
        added_elt['filename'] = filename = os.path.basename(song_path)
        added_elt['title'] = title
        added_elt['artist'] = artist
        added_elt['album'] = album
        added_elt['length'] = str(length)
        self.host.profiles[profile].xmlstream.send(mess)

        radio_data = self.radios[jid.JID(referee).userhost()] #FIXME: referee comes from Libervia's client side, it's unsecure
        radio_data['to_delete'][filename] = song_path #FIXME: works only because of the same host trick, see the note under the docstring  

    def playNext(self, room_jid, profile):
        """"Play next sont in queue if exists, and put a timer
        which trigger after the song has been played to play next one"""
        #TODO: need to check that there are still peoples in the room
        #      and clean the datas/stop the playlist if it's not the case
        #TODO: songs need to be erased once played or found invalids
        #      ==> unlink done the Q&D way with the same host trick (see above)
        radio_data = self.radios[room_jid.userhost()]
        queue = radio_data['queue']
        if not queue:
            #nothing left to play, we need to wait for uploads
            radio_data['playing'] = False
            return

        filename, length = queue.pop(0)
        mess = self.createRadiocolElt(room_jid)
        play_elt = mess.firstChildElement().addElement(('','play'))
        play_elt['filename'] = filename
        self.host.profiles[profile].xmlstream.send(mess)

        if not radio_data['upload'] and len(queue) < QUEUE_LIMIT:
            #upload is blocked and we now have resources to get more, we reactivate it
            mess = self.createRadiocolElt(room_jid)
            no_upload_elt = mess.firstChildElement().addElement(('','upload_ok'))
            self.host.profiles[profile].xmlstream.send(mess)
            radio_data['upload'] = True

        reactor.callLater(length, self.playNext, room_jid, profile)
        try:
            file_to_delete = radio_data['to_delete'][filename]
        except KeyError:
            error(_("INTERNAL ERROR: can't find full path of the song to delete"))
            return
        
        #we wait more than the song length to delete the file, to manage poorly reactive networks/clients  
        reactor.callLater(length + 90, unlink, file_to_delete) #FIXME: same host trick (see above)


    def radiocol_game_cmd(self, mess_elt, profile):
        #FIXME: we should check sender (is it referee ?) here before accepting commands
        from_jid = jid.JID(mess_elt['from']) 
        room_jid = jid.JID(from_jid.userhost())
        radio_elt = mess_elt.firstChildElement()
        radio_data = self.radios[room_jid.userhost()]
        occupants_data = radio_data['occupants_data']
        queue = radio_data['queue']
        
        for elt in radio_elt.elements():
            
            if elt.name == 'started': #new game created
                self.host.bridge.radiocolStarted(room_jid.userhost(), from_jid.full(), profile)
            elif elt.name == 'preload': #a song is in queue and must be preloaded
                self.host.bridge.radiocolPreload(room_jid.userhost(), elt['filename'], elt['title'], elt['artist'], elt['album'], profile)
            elif elt.name == 'play':
                self.host.bridge.radiocolPlay(room_jid.userhost(), elt['filename'], profile)
            elif elt.name == 'song_rejected': #a song has been refused
                self.host.bridge.radiocolSongRejected(room_jid.userhost(), elt['reason'], profile)
            elif elt.name == 'no_upload':
                self.host.bridge.radiocolNoUpload(room_jid.userhost(), profile)
            elif elt.name == 'upload_ok':
                self.host.bridge.radiocolUploadOk(room_jid.userhost(), profile)
            elif elt.name == 'song_added': #a song has been added
                #FIXME: we are KISS for the proof of concept: every song is added, to a limit of 3 in queue.
                #       Need to manage some sort of rules to allow peoples to send songs
                
                if len(queue) >= QUEUE_LIMIT:
                    #there are already too many songs in queue, we reject this one
                    mess = self.createRadiocolElt(room_jid)
                    reject_elt = mess.firstChildElement().addElement(('','song_rejected'))
                    reject_elt['sender'] = from_jid.resource
                    reject_elt['reason'] = "Too many songs in queue"
                    #FIXME: add an error code
                    self.host.profiles[profile].xmlstream.send(mess)
                    return
                    
                #The song is accepted and added in queue
                queue.append((elt['filename'], float(elt['length'])))

                if len(queue) >= QUEUE_LIMIT:
                    #We are at the limit, we refuse new upload until next play
                    mess = self.createRadiocolElt(room_jid)
                    no_upload_elt = mess.firstChildElement().addElement(('','no_upload'))
                    #FIXME: add an error code
                    self.host.profiles[profile].xmlstream.send(mess)
                    radio_data['upload'] = False


                mess = self.createRadiocolElt(room_jid)
                preload_elt = self.__create_preload_elt(from_jid.resource,
                                                        elt['filename'],
                                                        elt['title'],
                                                        elt['artist'],
                                                        elt['album'])
                mess.firstChildElement().addChild(preload_elt)
                self.host.profiles[profile].xmlstream.send(mess)
                if not radio_data['playing'] and len(queue) == 2:
                    #we have not started playing yet, and we have 2 songs in queue
                    #we can now start the party :)
                    radio_data['playing'] = True
                    self.playNext(room_jid, profile)
            else:
                error (_('Unmanaged game element: %s') % elt.name)
                
    def getHandler(self, profile):
            return RadiocolHandler(self)

class RadiocolHandler (XMPPHandler):
    implements(iwokkel.IDisco)
   
    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host

    def connectionInitialized(self):
        self.xmlstream.addObserver(RADIOC_REQUEST, self.plugin_parent.radiocol_game_cmd, profile = self.parent.profile)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=''):
        return [disco.DiscoFeature(NC_RADIOCOL)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=''):
        return []

