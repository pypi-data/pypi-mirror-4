#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SAT plugin for managing Quiz game 
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
from twisted.internet import protocol, defer, threads, reactor
from twisted.words.protocols.jabber import client, jid, xmlstream
from twisted.words.protocols.jabber import error as jab_error
from twisted.words.protocols.jabber.xmlstream import IQ
import random

from zope.interface import implements

from wokkel import disco, iwokkel, data_form
from sat.tools.xml_tools import dataForm2xml
from sat.tools.games import TarotCard

from time import time

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

MESSAGE = '/message'
NS_QG = 'http://www.goffi.org/protocol/quiz'
QG_TAG = 'quiz'
QG_REQUEST = MESSAGE + '/' + QG_TAG + '[@xmlns="' + NS_QG + '"]'

PLUGIN_INFO = {
"name": "Quiz game plugin",
"import_name": "Quiz",
"type": "Game",
"protocols": [],
"dependencies": ["XEP-0045", "XEP-0249"],
"main": "Quiz",
"handler": "yes",
"description": _("""Implementation of Quiz game""")
}


class Quiz():

    def __init__(self, host):
        info(_("Plugin Quiz initialization"))
        self.host = host
        self.games={}
        self.waiting_inv = {} #Invitation waiting for people to join to launch a game
        host.bridge.addMethod("quizGameLaunch", ".plugin", in_sign='ass', out_sign='', method=self.quizGameLaunch) #args: players, profile
        host.bridge.addMethod("quizGameCreate", ".plugin", in_sign='sass', out_sign='', method=self.quizGameCreate) #args: room_jid, players, profile
        host.bridge.addMethod("quizGameReady", ".plugin", in_sign='sss', out_sign='', method=self.newPlayerReady) #args: player, referee, profile
        host.bridge.addMethod("quizGameAnswer", ".plugin", in_sign='ssss', out_sign='', method=self.playerAnswer)
        host.bridge.addSignal("quizGameStarted", ".plugin", signature='ssass') #args: room_jid, referee, players, profile
        host.bridge.addSignal("quizGameNew", ".plugin",
                              signature='sa{ss}s',
                              doc = { 'summary': 'Start a new game',
                                      'param_0': "room_jid: jid of game's room",
                                      'param_1': "game_data: data of the game",
                                      'param_2': '%(doc_profile)s'})
        host.bridge.addSignal("quizGameQuestion", ".plugin",
                              signature = 'sssis',
                              doc = { 'summary': "Send the current question",
                                      'param_0': "room_jid: jid of game's room",
                                      'param_1': "question_id: question id",
                                      'param_2': "question: question to ask",
                                      'param_3': "timer: timer",
                                      'param_4': '%(doc_profile)s'})
        host.bridge.addSignal("quizGamePlayerBuzzed", ".plugin",
                              signature = 'ssbs',
                              doc = { 'summary': "A player just pressed the buzzer",
                                      'param_0': "room_jid: jid of game's room",
                                      'param_1': "player: player who pushed the buzzer",
                                      'param_2': "pause: should the game be paused ?",
                                      'param_3': '%(doc_profile)s'})
        host.bridge.addSignal("quizGamePlayerSays", ".plugin",
                              signature = 'sssis',
                              doc = { 'summary': "A player just pressed the buzzer",
                                      'param_0': "room_jid: jid of game's room",
                                      'param_1': "player: player who pushed the buzzer",
                                      'param_2': "text: what the player say",
                                      'param_3': "delay: how long, in seconds, the text must appear",
                                      'param_4': '%(doc_profile)s'})
        host.bridge.addSignal("quizGameAnswerResult", ".plugin",
                              signature = 'ssba{si}s',
                              doc = { 'summary': "Result of the just given answer",
                                      'param_0': "room_jid: jid of game's room",
                                      'param_1': "player: player who gave the answer",
                                      'param_2': "good_answer: True if the answer is right",
                                      'param_3': "score: dict of score with player as key",
                                      'param_4': '%(doc_profile)s'})
        host.bridge.addSignal("quizGameTimerExpired", ".plugin",
                              signature = 'ss',
                              doc = { 'summary': "Nobody answered the question in time",
                                      'param_0': "room_jid: jid of game's room",
                                      'param_1': '%(doc_profile)s'})
        host.bridge.addSignal("quizGameTimerRestarted", ".plugin",
                              signature = 'sis',
                              doc = { 'summary': "Nobody answered the question in time",
                                      'param_0': "room_jid: jid of game's room",
                                      'param_1': "time_left: time left before timer expiration",
                                      'param_2': '%(doc_profile)s'})
        host.trigger.add("MUC user joined", self.userJoinedTrigger)

    def createGameElt(self, to_jid, type="normal"):
        type = "normal" if to_jid.resource else "groupchat"
        elt = domish.Element((None,'message'))
        elt["to"] = to_jid.full()
        elt["type"] = type
        elt.addElement((NS_QG, QG_TAG))
        return elt

    def __game_data_to_xml(self, game_data):
        """Convert a game data dict to domish element"""
        game_data_elt = domish.Element((None,'game_data'))
        for data in game_data:
            data_elt = domish.Element((None,data))
            data_elt.addContent(game_data[data])
            game_data_elt.addChild(data_elt) 
        return game_data_elt

    def __xml_to_game_data(self, game_data_elt):
        """Convert a domish element with game_data to a dict"""
        game_data = {}
        for data_elt in game_data_elt.elements():
            game_data[data_elt.name] = unicode(data_elt)
        return game_data

    def __answer_result_to_signal_args(self, answer_result_elt):
        """Parse answer result element and return a tuple of signal arguments
        @param answer_result_elt: answer result element
        @return: (player, good_answer, score)"""
        score = {}
        for score_elt in answer_result_elt.children:
            score[score_elt['player']] = int(score_elt['score'])
        return (answer_result_elt['player'], answer_result_elt['good_answer'] == str(True), score)

    def __answer_result(self, player_answering, good_answer, game_data):
        """Convert a domish an answer_result element
        @param player_answering: player who gave the answer
        @param good_answer: True is the answer is right
        @param game_data: data of the game"""
        players_data = game_data['players_data']
        score = {}
        for player in game_data['players']:
            score[player] = players_data[player]['score']
        
        answer_result_elt = domish.Element((None,'answer_result'))
        answer_result_elt['player'] = player_answering
        answer_result_elt['good_answer'] = str(good_answer)
        
        for player in score:
            score_elt = domish.Element((None,"score"))
            score_elt['player'] = player
            score_elt['score'] = str(score[player])
            answer_result_elt.addChild(score_elt) 
        
        return answer_result_elt

    def __create_started_elt(self, players):
        """Create a game_started domish element"""
        started_elt = domish.Element((None,'started'))
        idx = 0
        for player in players:
            player_elt = domish.Element((None,'player'))
            player_elt.addContent(player)
            player_elt['index'] = str(idx)
            idx+=1
            started_elt.addChild(player_elt)
        return started_elt

    def __ask_question(self, question_id, question, timer):
        """Create a element for asking a question"""
        question_elt = domish.Element((None,'question'))
        question_elt['id'] = question_id
        question_elt['timer'] = str(timer)
        question_elt.addContent(question)
        return question_elt
    
    def __start_play(self, room_jid, game_data, profile):
        """Start the game (tell to the first player after dealer to play"""
        game_data['stage'] = "play"
        next_player_idx = game_data['current_player'] = (game_data['init_player'] + 1) % len(game_data['players']) #the player after the dealer start
        game_data['first_player'] = next_player = game_data['players'][next_player_idx]
        to_jid = jid.JID(room_jid.userhost()+"/"+next_player)
        mess = self.createGameElt(to_jid)
        yourturn_elt = mess.firstChildElement().addElement('your_turn')
        self.host.profiles[profile].xmlstream.send(mess)


    def userJoinedTrigger(self, room, user, profile):
        """This trigger is used to check if we are waiting people in this room,
        and to create a game if everybody is here"""
        _room_jid = room.occupantJID.userhostJID()
        if _room_jid in self.waiting_inv and len(room.roster) == 4:
            #When we have 4 people in the room, we create the game
            #TODO: check people identity
            players = room.roster.keys()
            del self.waiting_inv[_room_jid]
            self.quizGameCreate(_room_jid.userhost(), players, profile_key=profile)
        return True

    def quizGameLaunch(self, players, profile_key='@DEFAULT@'):
        """Launch a game: helper method to create a room, invite players, and create the quiz game
        @param players: list for players jid"""
        debug(_('Launching quiz game'))
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            error(_("Unknown profile"))
            return

        def quizRoomJoined(room):
            _room = room.occupantJID.userhostJID()
            for player in players:
                self.host.plugins["XEP-0249"].invite(jid.JID(player), room.occupantJID.userhostJID(), {"game":"Quiz"}, profile)
            self.waiting_inv[_room] = (time(), players) #TODO: remove invitation waiting for too long, using the time data
        
        def after_init(ignore):
            room_name = "sat_quiz_%s" % self.host.plugins["XEP-0045"].getUniqueName(profile_key)
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
            d = self.host.plugins["XEP-0045"].join(jid.JID("%s@%s" % (room_name, muc_service.userhost())), _jid.user, {}, profile).addCallback(quizRoomJoined)

        client = self.host.getClient(profile)
        if not client:
            error(_('No client for this profile key: %s') % profile_key)
            return
        client.client_initialized.addCallback(after_init)

    def quizGameCreate(self, room_jid_param, players, profile_key='@DEFAULT@'):
        """Create a new game
        @param room_jid_param: jid of the room
        @param players: list of players nick (nick must exist in the room)
        @param profile_key: %(doc_profile_key)s"""
        debug (_("Creating Quiz game"))
        room_jid = jid.JID(room_jid_param)
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            error (_("profile %s is unknown") % profile_key)
            return
        if self.games.has_key(room_jid):
            warning (_("Quiz game already started in room %s") % room_jid.userhost())
        else:
            room_nick = self.host.plugins["XEP-0045"].getRoomNick(room_jid.userhost(), profile)
            if not room_nick:
                error ('Internal error')
                return
            referee = room_jid.userhost() + '/' + room_nick
            status = {}
            players_data = {}
            for player in players:
                players_data[player] = {'score':0}
                status[player] = "init"
            self.games[room_jid.userhost()] = {'referee':referee, 'players':players, 'status':status, 'players_data':players_data, 'stage': None}
            for player in players:
                mess = self.createGameElt(jid.JID(room_jid.userhost()+'/'+player))
                mess.firstChildElement().addChild(self.__create_started_elt(players))
                self.host.profiles[profile].xmlstream.send(mess)

    def newPlayerReady(self, player, referee, profile_key='@DEFAULT@'):
        """Must be called when player is ready to start a new game"""
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            error (_("profile %s is unknown") % profile_key)
            return
        debug ('new player ready: %s' % profile)
        mess = self.createGameElt(jid.JID(referee))
        ready_elt = mess.firstChildElement().addElement('player_ready')
        ready_elt['player'] = player
        self.host.profiles[profile].xmlstream.send(mess)

    def playerAnswer(self, player, referee, answer, profile_key='@DEFAULT@'):
        """Called when a player give an answer"""
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            error (_("profile %s is unknown") % profile_key)
            return
        debug ('new player answer (%(profile)s): %(answer)s' % {'profile':profile, 'answer':answer})
        mess = self.createGameElt(jid.JID(referee))
        answer_elt = mess.firstChildElement().addElement('player_answer')
        answer_elt['player'] = player
        answer_elt.addContent(answer)
        self.host.profiles[profile].xmlstream.send(mess)

    def timerExpired(self, room_jid, profile):
        """Called when nobody answered the question in time"""
        game_data = self.games[room_jid.userhost()]
        game_data['stage'] = 'expired'
        mess = self.createGameElt(room_jid)
        expired_elt = mess.firstChildElement().addElement('timer_expired')
        self.host.profiles[profile].xmlstream.send(mess)
        reactor.callLater(4, self.askQuestion, room_jid, profile)

    def pauseTimer(self, room_jid):
        """Stop the timer and save the time left"""
        game_data = self.games[room_jid.userhost()]
        left = max(0, game_data["timer"].getTime() - time())
        game_data['timer'].cancel()
        game_data['time_left'] = int(left)
        game_data['previous_stage'] = game_data['stage']
        game_data['stage'] = "paused"

    def restartTimer(self, room_jid, profile):
        """Restart a timer with the saved time"""
        game_data = self.games[room_jid.userhost()]
        assert(game_data['time_left'] != None)
        mess = self.createGameElt(room_jid)
        restarted_elt = mess.firstChildElement().addElement('timer_restarted')
        restarted_elt["time_left"] = str(game_data['time_left'])
        self.host.profiles[profile].xmlstream.send(mess)
        game_data["timer"] = reactor.callLater(game_data['time_left'], self.timerExpired, room_jid, profile)
        game_data["time_left"] = None
        game_data['stage'] = game_data['previous_stage']
        del game_data['previous_stage']

    def askQuestion(self, room_jid, profile):
        """Ask a new question"""
        game_data = self.games[room_jid.userhost()]
        game_data['stage'] = "question"
        game_data['question_id'] = "1"
        timer = 30
        mess = self.createGameElt(room_jid)
        mess.firstChildElement().addChild(self.__ask_question(game_data['question_id'], u"Quel est l'âge du capitaine ?", timer))
        self.host.profiles[profile].xmlstream.send(mess)
        game_data["timer"] = reactor.callLater(timer, self.timerExpired, room_jid, profile)
        game_data["time_left"] = None

    def checkAnswer(self, room_jid, player, answer, profile): 
        """Check if the answer given is right"""
        game_data = self.games[room_jid.userhost()]
        players_data = game_data['players_data']
        good_answer =  game_data['question_id'] == "1" and answer=="42"
        players_data[player]['score'] += 1 if good_answer else -1
        players_data[player]['score'] = min(9, max(0, players_data[player]['score']))
        
        mess = self.createGameElt(room_jid)
        mess.firstChildElement().addChild(self.__answer_result(player, good_answer, game_data))
        self.host.profiles[profile].xmlstream.send(mess)
        
        if good_answer:
            reactor.callLater(4, self.askQuestion, room_jid, profile)
        else:
            reactor.callLater(4, self.restartTimer, room_jid, profile)

    def newGame(self, room_jid, profile):
        """Launch a new round"""
        debug (_('new Quiz game'))
        game_data = self.games[room_jid.userhost()]
        players = game_data['players']
        players_data = game_data['players_data']
        game_data['stage'] = "init"

        for player in players:
            players_data[player]['game_score'] = 0
        
        new_game_data = {"instructions": _(u"""Bienvenue dans cette partie rapide de quizz, le premier à atteindre le score de 9 remporte le jeu

Attention, tu es prêt ?""")}

        mess = self.createGameElt(room_jid)
        mess.firstChildElement().addChild(self.__game_data_to_xml(new_game_data))
        self.host.profiles[profile].xmlstream.send(mess)
        reactor.callLater(10, self.askQuestion, room_jid, profile)

    def quiz_game_cmd(self, mess_elt, profile):
        from_jid = jid.JID(mess_elt['from']) 
        room_jid = jid.JID(from_jid.userhost())
        game_elt = mess_elt.firstChildElement()
        game_data = self.games[room_jid.userhost()]
        players_data = game_data['players_data']
        
        for elt in game_elt.elements():
            
            if elt.name == 'started': #new game created
                players = []
                for player in elt.elements():
                    players.append(unicode(player))
                self.host.bridge.quizGameStarted(room_jid.userhost(), from_jid.full(), players, profile)
            
            elif elt.name == 'player_ready': #ready to play
                player = elt['player']
                status = self.games[room_jid.userhost()]['status']
                nb_players = len(self.games[room_jid.userhost()]['players'])
                status[player] = 'ready'
                debug (_('Player %(player)s is ready to start [status: %(status)s]') % {'player':player, 'status':status})
                if status.values().count('ready') == nb_players: #everybody is ready, we can start the game
                    self.newGame(room_jid, profile)

            elif elt.name == 'game_data':
                self.host.bridge.quizGameNew(room_jid.userhost(), self.__xml_to_game_data(elt), profile)
            
            elif elt.name == 'question': #A question is asked
                self.host.bridge.quizGameQuestion(room_jid.userhost(), elt["id"], unicode(elt), int(elt["timer"]), profile )
            
            elif elt.name == 'player_answer':
                player = elt['player']
                pause = game_data['stage'] == 'question' #we pause the game only if we are have a question at the moment
                #we first send a buzzer message
                mess = self.createGameElt(room_jid)
                buzzer_elt = mess.firstChildElement().addElement('player_buzzed')
                buzzer_elt['player'] = player
                buzzer_elt['pause'] = str(pause) 
                self.host.profiles[profile].xmlstream.send(mess)
                if pause:
                    self.pauseTimer(room_jid)
                    #and we send the player answer
                    mess = self.createGameElt(room_jid)
                    _answer = unicode(elt)
                    say_elt = mess.firstChildElement().addElement('player_says')
                    say_elt['player'] = player
                    say_elt.addContent(_answer)
                    say_elt['delay'] = "3"
                    reactor.callLater(2, self.host.profiles[profile].xmlstream.send, mess)
                    reactor.callLater(6, self.checkAnswer, room_jid, player, _answer, profile=profile)
                
            elif elt.name == 'player_buzzed':
                self.host.bridge.quizGamePlayerBuzzed(room_jid.userhost(), elt["player"], elt['pause'] == str(True), profile)
            
            elif elt.name == 'player_says':
                self.host.bridge.quizGamePlayerSays(room_jid.userhost(), elt["player"], unicode(elt), int(elt["delay"]), profile)
           
            elif elt.name == 'answer_result':
                player, good_answer, score = self.__answer_result_to_signal_args(elt)
                self.host.bridge.quizGameAnswerResult(room_jid.userhost(), player, good_answer, score, profile)
            
            elif elt.name == 'timer_expired':
                self.host.bridge.quizGameTimerExpired(room_jid.userhost(), profile)

            elif elt.name == 'timer_restarted':
                self.host.bridge.quizGameTimerRestarted(room_jid.userhost(), int(elt['time_left']), profile)

            else:
                error (_('Unmanaged game element: %s') % elt.name)
                
    def getHandler(self, profile):
            return QuizGameHandler(self)

class QuizGameHandler (XMPPHandler):
    implements(iwokkel.IDisco)
   
    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host

    def connectionInitialized(self):
        self.xmlstream.addObserver(QG_REQUEST, self.plugin_parent.quiz_game_cmd, profile = self.parent.profile)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=''):
        return [disco.DiscoFeature(NS_QG)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=''):
        return []

