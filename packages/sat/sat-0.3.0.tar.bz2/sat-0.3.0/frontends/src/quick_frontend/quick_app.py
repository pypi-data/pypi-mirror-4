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
from sat_frontends.bridge.DBus import DBusBridgeFrontend,BridgeExceptionNoService
from sat_frontends.quick_frontend.quick_utils import escapePrivate, unescapePrivate
from optparse import OptionParser

import sat_frontends.quick_frontend.constants

import gettext
gettext.install('sat_frontend', "../i18n", unicode=True)

class QuickApp(object):
    """This class contain the main methods needed for the frontend"""

    def __init__(self, single_profile=True):
        self.profiles = {}
        self.single_profile = single_profile
        self.check_options()
        
        ## bridge ##
        try:
            self.bridge=DBusBridgeFrontend()
        except BridgeExceptionNoService:
            print(_(u"Can't connect to SàT backend, are you sure it's launched ?"))
            import sys
            sys.exit(1)
        self.bridge.register("connected", self.connected)
        self.bridge.register("disconnected", self.disconnected)
        self.bridge.register("connectionError", self.connectionError)
        self.bridge.register("newContact", self.newContact)
        self.bridge.register("newMessage", self._newMessage)
        self.bridge.register("newAlert", self.newAlert)
        self.bridge.register("presenceUpdate", self.presenceUpdate)
        self.bridge.register("subscribe", self.subscribe)
        self.bridge.register("paramUpdate", self.paramUpdate)
        self.bridge.register("contactDeleted", self.contactDeleted)
        self.bridge.register("entityDataUpdated", self.entityDataUpdated)
        self.bridge.register("askConfirmation", self.askConfirmation)
        self.bridge.register("actionResult", self.actionResult)
        self.bridge.register("actionResultExt", self.actionResult)
        self.bridge.register("roomJoined", self.roomJoined, "plugin")
        self.bridge.register("roomLeft", self.roomLeft, "plugin")
        self.bridge.register("roomUserJoined", self.roomUserJoined, "plugin")
        self.bridge.register("roomUserLeft", self.roomUserLeft, "plugin")
        self.bridge.register("roomUserChangedNick", self.roomUserChangedNick, "plugin")
        self.bridge.register("roomNewSubject", self.roomNewSubject, "plugin")
        self.bridge.register("tarotGameStarted", self.tarotGameStarted, "plugin")
        self.bridge.register("tarotGameNew", self.tarotGameNew, "plugin")
        self.bridge.register("tarotGameChooseContrat", self.tarotChooseContrat, "plugin")
        self.bridge.register("tarotGameShowCards", self.tarotShowCards, "plugin")
        self.bridge.register("tarotGameYourTurn", self.tarotMyTurn, "plugin")
        self.bridge.register("tarotGameScore", self.tarotScore, "plugin")
        self.bridge.register("tarotGameCardsPlayed", self.tarotCardsPlayed, "plugin")
        self.bridge.register("tarotGameInvalidCards", self.tarotInvalidCards, "plugin")
        self.bridge.register("quizGameStarted", self.quizGameStarted, "plugin")
        self.bridge.register("quizGameNew", self.quizGameNew, "plugin")
        self.bridge.register("quizGameQuestion", self.quizGameQuestion, "plugin")
        self.bridge.register("quizGamePlayerBuzzed", self.quizGamePlayerBuzzed, "plugin")
        self.bridge.register("quizGamePlayerSays", self.quizGamePlayerSays, "plugin")
        self.bridge.register("quizGameAnswerResult", self.quizGameAnswerResult, "plugin")
        self.bridge.register("quizGameTimerExpired", self.quizGameTimerExpired, "plugin")
        self.bridge.register("quizGameTimerRestarted", self.quizGameTimerRestarted, "plugin")
        
        self.current_action_ids = set()
        self.current_action_ids_cb = {}
        self.media_dir = self.bridge.getConfig('','media_dir')
    
    def check_profile(self, profile):
        """Tell if the profile is currently followed by the application"""
        return profile in self.profiles.keys()

    def postInit(self):
        """Must be called after initialization is done, do all automatic task (auto plug profile)"""
        if self.options.profile:
            if not self.bridge.getProfileName(self.options.profile): 
                error(_("Trying to plug an unknown profile (%s)" % self.options.profile))
            else:
                self.plug_profile(self.options.profile)

    def check_options(self):
        """Check command line options"""
        usage=_("""
        %prog [options]

        %prog --help for options list
        """)
        parser = OptionParser(usage=usage)

        parser.add_option("-p", "--profile", help=_("Select the profile to use"))

        (self.options, args) = parser.parse_args()
        if self.options.profile:
            self.options.profile = self.options.profile.decode('utf-8')
        return args

    def _getParamError(self, ignore):
        error(_("Can't get profile parameter"))
    
    def plug_profile(self, profile_key='@DEFAULT@'):
        """Tell application which profile must be used"""
        if self.single_profile and self.profiles:
            error(_('There is already one profile plugged (we are in single profile mode) !'))
            return
        profile = self.bridge.getProfileName(profile_key)
        if not profile:
            error(_("The profile asked doesn't exist"))
            return
        if self.profiles.has_key(profile):
            warning(_("The profile is already plugged"))
            return
        self.profiles[profile]={}
        if self.single_profile:
            self.profile = profile
        
        ###now we get the essential params###
        self.bridge.asyncGetParamA("JabberID","Connection", profile_key=profile,
                                   callback=lambda _jid: self.plug_profile_2(_jid, profile), errback=self._getParamError)
        
    def plug_profile_2(self, _jid, profile):
        self.profiles[profile]['whoami'] = JID(_jid)
        self.bridge.asyncGetParamA("autoconnect","Connection", profile_key=profile,
                                   callback=lambda value: self.plug_profile_3(value=="true", profile), errback=self._getParamError)

    def plug_profile_3(self, autoconnect, profile):
        self.bridge.asyncGetParamA("Watched", "Misc", profile_key=profile,
                                   callback=lambda watched: self.plug_profile_4(watched, autoconnect, profile), errback=self._getParamError)

    def plug_profile_4(self, watched, autoconnect, profile):
        if autoconnect and not self.bridge.isConnected(profile):
            #Does the user want autoconnection ?
            self.bridge.asyncConnect(profile, callback=lambda: self.plug_profile_5(watched, autoconnect, profile), errback=lambda ignore: error(_('Error during autoconnection')))
        else:
            self.plug_profile_5(watched, autoconnect, profile)
    
    def plug_profile_5(self, watched, autoconnect, profile):
        self.profiles[profile]['watched'] = watched.split() #TODO: put this in a plugin

        ## misc ##
        self.profiles[profile]['onlineContact'] = set()  #FIXME: temporary

        #TODO: manage multi-profiles here
        if not self.bridge.isConnected(profile):
            self.setStatusOnline(False)
        else:
            self.setStatusOnline(True)

            ### now we fill the contact list ###
            for contact in self.bridge.getContacts(profile):
                self.newContact(*contact, profile=profile)

            presences = self.bridge.getPresenceStatus(profile)
            for contact in presences:
                for res in presences[contact]:
                    jabber_id = contact+('/'+res if res else '')
                    show = presences[contact][res][0]
                    priority = presences[contact][res][1]
                    statuses = presences[contact][res][2]
                    self.presenceUpdate(jabber_id, show, priority, statuses, profile)
                    data = self.bridge.getEntityData(contact, ['avatar','nick'], profile)
                    for key in ('avatar', 'nick'):
                        if key in data:
                            self.entityDataUpdated(contact, key, data[key], profile)

            #The waiting subscription requests
            waitingSub = self.bridge.getWaitingSub(profile)
            for sub in waitingSub:
                self.subscribe(waitingSub[sub], sub, profile)

            #Now we open the MUC window where we already are:
            for room_args in self.bridge.getRoomsJoined(profile):
                self.roomJoined(*room_args, profile=profile)

            for subject_args in self.bridge.getRoomsSubjects(profile):
                self.roomNewSubject(*subject_args, profile=profile)

            #Finaly, we get the waiting confirmation requests
            for confirm_id, confirm_type, data in self.bridge.getWaitingConf(profile):
                self.askConfirmation(confirm_id, confirm_type, data, profile)

        

    def unplug_profile(self, profile):
        """Tell the application to not follow anymore the profile"""
        if not profile in self.profiles:
            warning (_("This profile is not plugged"))
            return
        self.profiles.remove(profile)

    def clear_profile(self):
        self.profiles.clear()

    def connected(self, profile):
        """called when the connection is made"""
        if not self.check_profile(profile):
            return
        debug(_("Connected"))
        self.setStatusOnline(True)

    def disconnected(self, profile):
        """called when the connection is closed"""
        if not self.check_profile(profile):
            return
        debug(_("Disconnected"))
        self.contact_list.clearContacts()
        self.setStatusOnline(False)
    
    def connectionError(self, error_type, profile):
        """called when something goest wrong with the connection"""
        if not self.check_profile(profile):
            return
        debug(_("Connection Error"))
        self.disconnected(profile)
        if error_type == "AUTH_ERROR":
            self.showDialog(_("Can't connect to account, please check your password"), _("Connection error"), "error")
        else:
            error(_('FIXME: error_type %s not implemented') % error_type)

    def newContact(self, JabberId, attributes, groups, profile):
        if not self.check_profile(profile):
            return
        entity=JID(JabberId)
        _groups = list(groups)
        self.contact_list.replace(entity, _groups, attributes)

    def _newMessage(self, from_jid_s, msg, _type, to_jid_s, extra, profile):
        """newMessage premanagement: a dirty hack to manage private messages
        if a private MUC message is detected, from_jid or to_jid is prefixed and resource is escaped"""
        if not self.check_profile(profile):
            return
        from_jid = JID(from_jid_s)
        to_jid = JID(to_jid_s)
        
        from_me = from_jid.short == self.profiles[profile]['whoami'].short
        win = to_jid if from_me else from_jid
        
        if _type != "groupchat" and self.contact_list.getSpecial(win) == "MUC":
            #we have a private message in a MUC room
            #XXX: normaly we use bare jid as key, here we need the full jid
            #     so we cheat by replacing the "/" before the resource by
            #     a "@", so the jid is invalid, 
            new_jid = escapePrivate(win)
            if from_me:
                to_jid = new_jid
            else:
                from_jid = new_jid
            if new_jid not in self.contact_list:
                self.contact_list.add(new_jid)

        self.newMessage(from_jid, to_jid, msg, _type, extra, profile)
    
    def newMessage(self, from_jid, to_jid, msg, _type, extra, profile):
        from_me = from_jid.short == self.profiles[profile]['whoami'].short
        win = to_jid if from_me else from_jid
        
        self.current_action_ids = set()
        self.current_action_ids_cb = {}

        timestamp = extra.get('archive')
        self.chat_wins[win.short].printMessage(from_jid, msg, profile, float(timestamp) if timestamp else '')

    def sendMessage(self, to_jid, message, subject='', mess_type="auto", profile_key="@DEFAULT@"):
        if to_jid.startswith(const_PRIVATE_PREFIX):
            to_jid = unescapePrivate(to_jid)
            mess_type = "chat"
        self.bridge.sendMessage(to_jid, message, subject, mess_type, profile_key)

    def newAlert(self, msg, title, alert_type, profile):
        if not self.check_profile(profile):
            return
        assert alert_type in ['INFO','ERROR']
        self.showDialog(unicode(msg),unicode(title),alert_type.lower())

    
    def setStatusOnline(self, online=True):
        pass

    def presenceUpdate(self, jabber_id, show, priority, statuses, profile):
        if not self.check_profile(profile):
            return
        debug (_("presence update for %(jid)s (show=%(show)s, priority=%(priority)s, statuses=%(statuses)s) [profile:%(profile)s]") % {'jid':jabber_id, 'show':show, 'priority':priority, 'statuses':statuses, 'profile':profile});
        from_jid=JID(jabber_id)
        debug ("from_jid.short=%(from_jid)s whoami.short=%(whoami)s" % {'from_jid':from_jid.short, 'whoami':self.profiles[profile]['whoami'].short})

        if from_jid.short==self.profiles[profile]['whoami'].short:
            if not type:
                self.setStatusOnline(True)
            elif type=="unavailable":
                self.setStatusOnline(False)
            return

        self.contact_list.updatePresence(from_jid, show, priority, statuses) 
            
        if show != 'unavailable':
            
            #FIXME: must be moved in a plugin
            if from_jid.short in self.profiles[profile]['watched'] and not from_jid.short in self.profiles[profile]['onlineContact']:
                self.showAlert(_("Watched jid [%s] is connected !") % from_jid.short)

            self.profiles[profile]['onlineContact'].add(from_jid)  #FIXME onlineContact is useless with CM, must be removed
           
            #TODO: vcard data (avatar)

        if show=="unavailable" and from_jid in self.profiles[profile]['onlineContact']:
            self.profiles[profile]['onlineContact'].remove(from_jid)
    
    def roomJoined(self, room_jid, room_nicks, user_nick, profile):
        """Called when a MUC room is joined"""
        if not self.check_profile(profile):
            return
        debug (_("Room [%(room_jid)s] joined by %(profile)s, users presents:%(users)s") % {'room_jid':room_jid, 'profile': profile, 'users':room_nicks})
        self.chat_wins[room_jid].setUserNick(user_nick)
        self.chat_wins[room_jid].setType("group")
        self.chat_wins[room_jid].id = room_jid
        self.chat_wins[room_jid].setPresents(list(set([user_nick]+room_nicks)))
        self.contact_list.setSpecial(JID(room_jid), "MUC")

    def roomLeft(self, room_jid_s, profile):
        """Called when a MUC room is left"""
        if not self.check_profile(profile):
            return
        debug (_("Room [%(room_jid)s] left by %(profile)s") % {'room_jid':room_jid_s, 'profile': profile})
        del self.chat_wins[room_jid_s]
        self.contact_list.remove(JID(room_jid_s))

    def roomUserJoined(self, room_jid, user_nick, user_data, profile):
        """Called when an user joined a MUC room"""
        if not self.check_profile(profile):
            return
        if self.chat_wins.has_key(room_jid):
            self.chat_wins[room_jid].replaceUser(user_nick)
            debug (_("user [%(user_nick)s] joined room [%(room_jid)s]") % {'user_nick':user_nick, 'room_jid':room_jid})

    def roomUserLeft(self, room_jid, user_nick, user_data, profile):
        """Called when an user joined a MUC room"""
        if not self.check_profile(profile):
            return
        if self.chat_wins.has_key(room_jid):
            self.chat_wins[room_jid].removeUser(user_nick)
            debug (_("user [%(user_nick)s] left room [%(room_jid)s]") % {'user_nick':user_nick, 'room_jid':room_jid})

    def roomUserChangedNick(self, room_jid, old_nick, new_nick, profile):
        """Called when an user joined a MUC room"""
        if not self.check_profile(profile):
            return
        if self.chat_wins.has_key(room_jid):
            self.chat_wins[room_jid].changeUserNick(old_nick, new_nick)
            debug (_("user [%(old_nick)s] is now known as [%(new_nick)s] in room [%(room_jid)s]") % {'old_nick':old_nick, 'new_nick':new_nick, 'room_jid':room_jid})

    def roomNewSubject(self, room_jid, subject, profile):
        """Called when subject of MUC room change"""
        if not self.check_profile(profile):
            return
        if self.chat_wins.has_key(room_jid):
            self.chat_wins[room_jid].setSubject(subject)
            debug (_("new subject for room [%(room_jid)s]: %(subject)s") % {'room_jid':room_jid, "subject":subject})
    
    def tarotGameStarted(self, room_jid, referee, players, profile):
        if not self.check_profile(profile):
            return
        debug  (_("Tarot Game Started \o/"))
        if self.chat_wins.has_key(room_jid):
            self.chat_wins[room_jid].startGame("Tarot", referee, players)
            debug (_("new Tarot game started by [%(referee)s] in room [%(room_jid)s] with %(players)s") % {'referee':referee, 'room_jid':room_jid, 'players':[str(player) for player in players]})
       
    def tarotGameNew(self, room_jid, hand, profile):
        if not self.check_profile(profile):
            return
        debug (_("New Tarot Game"))
        if self.chat_wins.has_key(room_jid):
            self.chat_wins[room_jid].getGame("Tarot").newGame(hand)

    def tarotChooseContrat(self, room_jid, xml_data, profile):
        """Called when the player has to select his contrat"""
        if not self.check_profile(profile):
            return
        debug (_("Tarot: need to select a contrat"))
        if self.chat_wins.has_key(room_jid):
            self.chat_wins[room_jid].getGame("Tarot").chooseContrat(xml_data)

    def tarotShowCards(self, room_jid, game_stage, cards, data, profile):
        if not self.check_profile(profile):
            return
        debug (_("Show cards"))
        if self.chat_wins.has_key(room_jid):
            self.chat_wins[room_jid].getGame("Tarot").showCards(game_stage, cards, data)

    def tarotMyTurn(self, room_jid, profile):
        if not self.check_profile(profile):
            return
        debug (_("My turn to play"))
        if self.chat_wins.has_key(room_jid):
            self.chat_wins[room_jid].getGame("Tarot").myTurn()
    
    def tarotScore(self, room_jid, xml_data, winners, loosers, profile): 
        """Called when the game is finished and the score are updated"""
        if not self.check_profile(profile):
            return
        debug (_("Tarot: score received"))
        if self.chat_wins.has_key(room_jid):
            self.chat_wins[room_jid].getGame("Tarot").showScores(xml_data, winners, loosers)

    def tarotCardsPlayed(self, room_jid, player, cards, profile):
        if not self.check_profile(profile):
            return
        debug (_("Card(s) played (%(player)s): %(cards)s") % {"player":player, "cards":cards})
        if self.chat_wins.has_key(room_jid):
            self.chat_wins[room_jid].getGame("Tarot").cardsPlayed(player, cards)
   
    def tarotInvalidCards(self, room_jid, phase, played_cards, invalid_cards, profile):
        if not self.check_profile(profile):
            return
        debug (_("Cards played are not valid: %s") % invalid_cards)
        if self.chat_wins.has_key(room_jid):
            self.chat_wins[room_jid].getGame("Tarot").invalidCards(phase, played_cards, invalid_cards)
  
    def quizGameStarted(self, room_jid, referee, players, profile):
        if not self.check_profile(profile):
            return
        debug  (_("Quiz Game Started \o/"))
        if self.chat_wins.has_key(room_jid):
            self.chat_wins[room_jid].startGame("Quiz", referee, players)
            debug (_("new Quiz game started by [%(referee)s] in room [%(room_jid)s] with %(players)s") % {'referee':referee, 'room_jid':room_jid, 'players':[str(player) for player in players]})
       
    def quizGameNew(self, room_jid, data, profile):
        if not self.check_profile(profile):
            return
        debug (_("New Quiz Game"))
        if self.chat_wins.has_key(room_jid):
            self.chat_wins[room_jid].getGame("Quiz").quizGameNew(data)

    def quizGameQuestion(self, room_jid, question_id, question, timer, profile):
        """Called when a new question is asked"""
        if not self.check_profile(profile):
            return
        debug (_(u"Quiz: new question: %s") % question)
        if self.chat_wins.has_key(room_jid):
            self.chat_wins[room_jid].getGame("Quiz").quizGameQuestion(question_id, question, timer)

    def quizGamePlayerBuzzed(self, room_jid, player, pause, profile):
        """Called when a player pushed the buzzer"""
        if not self.check_profile(profile):
            return
        if self.chat_wins.has_key(room_jid):
            self.chat_wins[room_jid].getGame("Quiz").quizGamePlayerBuzzed(player, pause)

    def quizGamePlayerSays(self, room_jid, player, text, delay, profile):
        """Called when a player say something"""
        if not self.check_profile(profile):
            return
        if self.chat_wins.has_key(room_jid):
            self.chat_wins[room_jid].getGame("Quiz").quizGamePlayerSays(player, text, delay)

    def quizGameAnswerResult(self, room_jid, player, good_answer, score, profile):
        """Called when a player say something"""
        if not self.check_profile(profile):
            return
        if self.chat_wins.has_key(room_jid):
            self.chat_wins[room_jid].getGame("Quiz").quizGameAnswerResult(player, good_answer, score)
    
    def quizGameTimerExpired(self, room_jid, profile):
        """Called when nobody answered the question in time"""
        if not self.check_profile(profile):
            return
        if self.chat_wins.has_key(room_jid):
            self.chat_wins[room_jid].getGame("Quiz").quizGameTimerExpired()

    def quizGameTimerRestarted(self, room_jid, time_left, profile):
        """Called when the question is not answered, and we still have time"""
        if not self.check_profile(profile):
            return
        if self.chat_wins.has_key(room_jid):
            self.chat_wins[room_jid].getGame("Quiz").quizGameTimerRestarted(time_left)

    def _subscribe_cb(self, answer, data):
        entity, profile = data
        if answer:
            self.bridge.subscription("subscribed", entity.short, profile_key = profile)
        else:
            self.bridge.subscription("unsubscribed", entity.short, profile_key = profile)

    def subscribe(self, type, raw_jid, profile):
        """Called when a subsciption management signal is received"""
        if not self.check_profile(profile):
            return
        entity = JID(raw_jid)
        if type=="subscribed":
            # this is a subscription confirmation, we just have to inform user
            self.showDialog(_("The contact %s has accepted your subscription") % entity.short, _('Subscription confirmation'))
        elif type=="unsubscribed":
            # this is a subscription refusal, we just have to inform user
            self.showDialog(_("The contact %s has refused your subscription") % entity.short, _('Subscription refusal'), 'error')
        elif type=="subscribe":
            # this is a subscriptionn request, we have to ask for user confirmation
            answer = self.showDialog(_("The contact %s wants to subscribe to your presence.\nDo you accept ?") % entity.short, _('Subscription confirmation'), 'yes/no', answer_cb = self._subscribe_cb, answer_data=(entity, profile))

    def showDialog(self, message, title, type="info", answer_cb = None):
        raise NotImplementedError
    
    def showAlert(self, message):
        pass  #FIXME
    
    def paramUpdate(self, name, value, namespace, profile):
        if not self.check_profile(profile):
            return
        debug(_("param update: [%(namespace)s] %(name)s = %(value)s") % {'namespace':namespace, 'name':name, 'value':value})
        if (namespace,name) == ("Connection", "JabberID"):
            debug (_("Changing JID to %s"), value)
            self.profiles[profile]['whoami']=JID(value)
        elif (namespace,name) == ("Misc", "Watched"):
            self.profiles[profile]['watched']=value.split()

    def contactDeleted(self, jid, profile):
        if not self.check_profile(profile):
            return
        target = JID(jid)
        self.contact_list.remove(target)
        try:
            self.profiles[profile]['onlineContact'].remove(target.short)
        except KeyError:
            pass

    def entityDataUpdated(self, jid_str, key, value, profile):
        if not self.check_profile(profile):
            return
        jid = JID(jid_str)
        if key == "nick":
            if jid in self.contact_list:
                self.contact_list.setCache(jid, 'nick', value)
                self.contact_list.replace(jid)
        elif key == "avatar":
            if jid in self.contact_list:
                filename = self.bridge.getAvatarFile(value)
                self.contact_list.setCache(jid, 'avatar', filename)
                self.contact_list.replace(jid)

    def askConfirmation(self, confirm_id, confirm_type, data, profile):
        raise NotImplementedError
    
    def actionResult(self, type, id, data):
        raise NotImplementedError

    def onExit(self):
        """Must be called when the frontend is terminating"""
        #TODO: mange multi-profile here
        try:
            if self.bridge.isConnected(self.profile):
                if self.bridge.getParamA("autodisconnect","Connection", profile_key=self.profile) == "true":
                    #The user wants autodisconnection
                    self.bridge.disconnect(self.profile)
        except:
            pass
