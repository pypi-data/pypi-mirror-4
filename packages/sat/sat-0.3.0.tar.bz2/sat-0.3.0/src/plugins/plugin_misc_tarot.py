#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SAT plugin for managing French Tarot game
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
from twisted.words.protocols.jabber import jid
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
NS_CG = 'http://www.goffi.org/protocol/card_game'
CG_TAG = 'card_game'
CG_REQUEST = MESSAGE + '/' + CG_TAG + '[@xmlns="' + NS_CG + '"]'

PLUGIN_INFO = {
"name": "Tarot cards plugin",
"import_name": "Tarot",
"type": "Misc",
"protocols": [],
"dependencies": ["XEP-0045", "XEP-0249"],
"main": "Tarot",
"handler": "yes",
"description": _("""Implementation of Tarot card game""")
}


class Tarot():

    def __init__(self, host):
        info(_("Plugin Tarot initialization"))
        self.host = host
        self.games={}
        self.waiting_inv = {} #Invitation waiting for people to join to launch a game
        self.contrats = [_('Passe'), _('Petite'), _('Garde'), _('Garde Sans'), _('Garde Contre')]
        host.bridge.addMethod("tarotGameLaunch", ".plugin", in_sign='ass', out_sign='', method=self.launchGame) #args: room_jid, players, profile
        host.bridge.addMethod("tarotGameCreate", ".plugin", in_sign='sass', out_sign='', method=self.createGame) #args: room_jid, players, profile
        host.bridge.addMethod("tarotGameReady", ".plugin", in_sign='sss', out_sign='', method=self.newPlayerReady) #args: player, referee, profile
        host.bridge.addMethod("tarotGameContratChoosed", ".plugin", in_sign='ssss', out_sign='', method=self.contratChoosed) #args: player, referee, contrat, profile
        host.bridge.addMethod("tarotGamePlayCards", ".plugin", in_sign='ssa(ss)s', out_sign='', method=self.play_cards) #args: player, referee, cards, profile
        host.bridge.addSignal("tarotGameStarted", ".plugin", signature='ssass') #args: room_jid, referee, players, profile
        host.bridge.addSignal("tarotGameNew", ".plugin", signature='sa(ss)s') #args: room_jid, hand, profile
        host.bridge.addSignal("tarotGameChooseContrat", ".plugin", signature='sss') #args: room_jid, xml_data, profile
        host.bridge.addSignal("tarotGameShowCards", ".plugin", signature='ssa(ss)a{ss}s') #args: room_jid, type ["chien", "poignée",...], cards, data[dict], profile
        host.bridge.addSignal("tarotGameCardsPlayed", ".plugin", signature='ssa(ss)s') #args: room_jid, player, type ["chien", "poignée",...], cards, data[dict], profile
        host.bridge.addSignal("tarotGameYourTurn", ".plugin", signature='ss') #args: room_jid, profile
        host.bridge.addSignal("tarotGameScore", ".plugin", signature='ssasass') #args: room_jid, xml_data, winners (list of nicks), loosers (list of nicks), profile
        host.bridge.addSignal("tarotGameInvalidCards", ".plugin", signature='ssa(ss)a(ss)s') #args: room_jid, game phase, played_cards, invalid_cards, profile
        host.trigger.add("MUC user joined", self.userJoinedTrigger)
        self.deck_ordered = []
        for value in ['excuse']+map(str,range(1,22)):
            self.deck_ordered.append(TarotCard(("atout",value)))
        for suit in ["pique", "coeur", "carreau", "trefle"]:
            for value in map(str,range(1,11))+["valet","cavalier","dame","roi"]:
                self.deck_ordered.append(TarotCard((suit, value)))

    def createGameElt(self, to_jid, type="normal"):
        type = "normal" if to_jid.resource else "groupchat"
        elt = domish.Element((None,'message'))
        elt["to"] = to_jid.full()
        elt["type"] = type
        elt.addElement((NS_CG, CG_TAG))
        return elt

    def __card_list_to_xml(self, cards_list, elt_name):
        """Convert a card list to domish element"""
        cards_list_elt = domish.Element((None,elt_name))
        for card in cards_list:
            card_elt = domish.Element((None,'card'))
            card_elt['suit'] = card.suit
            card_elt['value'] = card.value
            cards_list_elt.addChild(card_elt) 
        return cards_list_elt

    def __xml_to_list(self, cards_list_elt):
        """Convert a domish element with cards to a list of tuples"""
        cards_list = []
        for card in cards_list_elt.elements():
            cards_list.append((card['suit'], card['value']))
        return cards_list
            

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

    def __ask_contrat(self):
        """Create a element for asking contrat"""
        contrat_elt = domish.Element((None,'contrat'))
        form = data_form.Form('form', title=_('contrat selection'))
        field = data_form.Field('list-single', 'contrat', options=map(data_form.Option, self.contrats), required=True)
        form.addField(field)
        contrat_elt.addChild(form.toElement())
        return contrat_elt

    def __give_scores(self, scores, winners, loosers):
        """Create an element to give scores
        @param scores: unicode (can contain line feed)
        @param winners: list of unicode nicks of winners
        @param loosers: list of unicode nicks of loosers"""

        score_elt = domish.Element((None,'score'))
        form = data_form.Form('form', title=_('scores'))
        for line in scores.split('\n'):
            field = data_form.Field('fixed', value = line)
            form.addField(field)
        score_elt.addChild(form.toElement())
        for winner in winners:
            winner_elt = domish.Element((None,'winner'))
            winner_elt.addContent(winner)
            score_elt.addChild(winner_elt)
        for looser in loosers:
            looser_elt = domish.Element((None,'looser'))
            looser_elt.addContent(looser)
            score_elt.addChild(looser_elt)
        return score_elt

    def __invalid_cards_elt(self, played_cards, invalid_cards, game_phase):
        """Create a element for invalid_cards error
        @param list_cards: list of Card
        @param game_phase: phase of the game ['ecart', 'play']"""
        error_elt = domish.Element((None,'error'))
        played_elt = self.__card_list_to_xml(played_cards, 'played')
        invalid_elt = self.__card_list_to_xml(invalid_cards, 'invalid')
        error_elt['type'] = 'invalid_cards'
        error_elt['phase'] = game_phase
        error_elt.addChild(played_elt)
        error_elt.addChild(invalid_elt)
        return error_elt
        
    def __next_player(self, game_data, next_pl = None):
        """Increment player number & return player name
        @param next_pl: if given, then next_player is forced to this one
        """
        if next_pl:
            game_data['current_player'] = game_data['players'].index(next_pl)
            return next_pl
        else:
            pl_idx = game_data['current_player'] = (game_data['current_player'] + 1) % len(game_data['players'])
            return game_data['players'][pl_idx]

    def __winner(self, game_data):
        """give the nick of the player who win this trick"""
        players_data = game_data['players_data']
        first = game_data['first_player']
        first_idx = game_data['players'].index(first) 
        suit_asked = None
        strongest = None
        winner = None
        for idx in [(first_idx + i) % 4 for i in range(4)]:
            player = game_data['players'][idx]
            card = players_data[player]['played']
            if card.value == "excuse":
                continue
            if suit_asked == None:
                suit_asked = card.suit
            if (card.suit == suit_asked or card.suit == "atout") and card > strongest:
                strongest = card
                winner = player
        assert winner
        return winner

    def __excuse_hack(self, game_data, played, winner):
        """give a low card to other team and keep excuse if trick is lost
        @param game_data: data of the game
        @param played: cards currently on the table
        @param winner: nick of the trick winner"""
        #TODO: manage the case where excuse is played on the last trick (and lost)
        players_data = game_data['players_data']
        excuse = TarotCard(("atout","excuse"))

        #we first check if the Excuse was already played
        #and if somebody is waiting for a card
        for player in game_data['players']:
            if players_data[player]['wait_for_low']:
                #the excuse owner has to give a card to somebody
                if winner == player:
                    #the excuse owner win the trick, we check if we have something to give
                    for card in played:
                        if card.points == 0.5:
                            pl_waiting = players_data[player]['wait_for_low']
                            played.remove(card)
                            players_data[pl_waiting]['levees'].append(card)
                            debug (_('Player %(excuse_owner)s give %(card_waited)s to %(player_waiting)s for Excuse compensation') % {"excuse_owner":player, "card_waited": card, "player_waiting":pl_waiting})
                            return
                return

        if not excuse in played:
            #the Excuse is not on the table, nothing to do
            return
        
        excuse_player = None #Who has played the Excuse ?
        for player in game_data['players']:
            if players_data[player]['played'] == excuse:
                excuse_player = player
                break
            
        if excuse_player == winner:
            return #the excuse player win the trick, nothing to do
        
        #first we remove the excuse from played cards
        played.remove(excuse)
        #then we give it back to the original owner 
        owner_levees = players_data[excuse_player]['levees']
        owner_levees.append(excuse)
        #finally we give a low card to the trick winner
        low_card = None
        #We look backward in cards won by the Excuse owner to
        #find a low value card
        for card_idx in range(len(owner_levees)-1, -1, -1):
            if owner_levees[card_idx].points == 0.5:
                low_card = owner_levees[card_idx]
                del owner_levees[card_idx]
                players_data[winner]['levees'].append(low_card)
                debug (_('Player %(excuse_owner)s give %(card_waited)s to %(player_waiting)s for Excuse compensation') % {"excuse_owner":excuse_player, "card_waited": low_card, "player_waiting":winner})
                break
        if not low_card: #The player has no low card yet
            #TODO: manage case when player never win a trick with low card
            players_data[excuse_player]['wait_for_low'] = winner
            debug(_("%(excuse_owner)s keep the Excuse but has not card to give, %(winner)s is waiting for one") % {'excuse_owner':excuse_player, 'winner':winner})


    def __draw_game(self, game_data):
        """The game is draw, no score change
        @param game_data: data of the game
        @return: tuple with (string victory message, list of winners, list of loosers)"""
        players_data = game_data['players_data']
        scores_str = _('Draw game')
        scores_str+='\n'
        for player in game_data['players']:
            scores_str+=_("\n--\n%(player)s:\nscore for this game ==> %(score_game)i\ntotal score ==> %(total_score)i") % {'player':player, 'score_game':0, 'total_score': players_data[player]['score']}
        debug(scores_str)
 
        return (scores_str, [], [])

    
    def __calculate_scores(self, game_data):
        """The game is finished, time to know who won :)
        @param game_data: data of the game
        @return: tuple with (string victory message, list of winners, list of loosers)"""
        players_data = game_data['players_data']
        levees = players_data[game_data['attaquant']]['levees']
        score = 0
        nb_bouts = 0
        bouts = []
        for card in levees:
            if card.bout:
                nb_bouts +=1
                bouts.append(card.value)
            score += card.points
        
        #We we do a basic check on score calculation
        check_score = 0
        defenseurs = game_data['players'][:]
        defenseurs.remove(game_data['attaquant'])
        for defenseur in defenseurs:
            for card in players_data[defenseur]['levees']:
                check_score+=card.points
        if game_data['contrat'] == "Garde Contre":
            for card in game_data['chien']:
                check_score+=card.points
        assert (score + check_score == 91)
        
        point_limit = None
        if nb_bouts == 3:
            point_limit = 36
        elif nb_bouts == 2:
            point_limit = 41
        elif nb_bouts == 1:
            point_limit = 51
        else:
            point_limit = 56
        if game_data['contrat'] == 'Petite':
            contrat_mult = 1
        elif game_data['contrat'] == 'Garde':
            contrat_mult = 2
        elif game_data['contrat'] == 'Garde Sans':
            contrat_mult = 4
        elif game_data['contrat'] == 'Garde Contre':
            contrat_mult = 6
        else:
            error(_('INTERNAL ERROR: contrat not managed (mispelled ?)'))
            assert(False)

        victory = (score >= point_limit)
        margin = abs(score - point_limit)
        points_defenseur = (margin + 25) * contrat_mult * (-1 if victory else 1)
        winners = []
        loosers = []
        player_score = {}
        for player in game_data['players']:
            #TODO: adjust this for 3 and 5 players variants
            #TODO: manage bonuses (petit au bout, poignée, chelem)
            player_score[player] = points_defenseur if player != game_data['attaquant'] else points_defenseur * -3
            players_data[player]['score'] += player_score[player] #we add score of this game to the global score
            if player_score[player] > 0:
                winners.append(player)
            else:
                loosers.append(player)

        scores_str = _('The attacker (%(attaquant)s) makes %(points)i and needs to make %(point_limit)i (%(nb_bouts)s oulder%(plural)s%(separator)s%(bouts)s): he %(victory)s') % {'attaquant':game_data['attaquant'], 'points':score, 'point_limit':point_limit, 'nb_bouts': nb_bouts, 'plural': 's' if nb_bouts>1 else '', 'separator':': ' if nb_bouts != 0 else '', 'bouts':','.join(map(str,bouts)), 'victory': 'win' if victory else 'loose'}
        scores_str+='\n'
        for player in game_data['players']:
            scores_str+=_("\n--\n%(player)s:\nscore for this game ==> %(score_game)i\ntotal score ==> %(total_score)i") % {'player':player, 'score_game':player_score[player], 'total_score': players_data[player]['score']}
        debug(scores_str)
 
        return (scores_str, winners, loosers)

    def __invalid_cards(self, game_data, cards):
        """Checks that the player has the right to play what he wants to
        @param game_data: Game data
        @param cards: cards the player want to play
        @return forbidden_cards cards or empty list if cards are ok"""
        forbidden_cards = []
        if game_data['stage'] == 'ecart':
            for card in cards:
                if card.bout or card.value=="roi":
                    forbidden_cards.append(card)
                #TODO: manage case where atouts (trumps) are in the dog
        elif game_data['stage'] == 'play':
            biggest_atout = None
            suit_asked = None
            players = game_data['players']
            players_data = game_data['players_data']
            idx = players.index(game_data['first_player'])
            current_idx = game_data['current_player']
            current_player = players[current_idx]
            if idx == current_idx:
                #the player is the first to play, he can play what he wants
                return forbidden_cards
            while (idx != current_idx):
                player = players[idx]
                played_card = players_data[player]['played']
                if not suit_asked and played_card.value != "excuse":
                    suit_asked = played_card.suit
                if played_card.suit == "atout" and played_card > biggest_atout:
                    biggest_atout = played_card
                idx = (idx + 1) % len(players)
            has_suit = False #True if there is one card of the asked suit in the hand of the player
            has_atout = False
            biggest_hand_atout = None

            for hand_card in game_data['hand'][current_player]:
                if hand_card.suit == suit_asked:
                    has_suit = True
                if hand_card.suit == "atout":
                    has_atout = True
                if hand_card.suit == "atout" and hand_card > biggest_hand_atout:
                    biggest_hand_atout = hand_card

            assert len(cards) == 1
            card = cards[0]
            if card.suit != suit_asked and has_suit and card.value != "excuse":
                forbidden_cards.append(card)
                return forbidden_cards
            if card.suit != suit_asked and card.suit != "atout" and has_atout:
                forbidden_cards.append(card)
                return forbidden_cards
            if card.suit == "atout" and card < biggest_atout and biggest_hand_atout > biggest_atout and card.value != "excuse":
                forbidden_cards.append(card)
        else:
            error(_('Internal error: unmanaged game stage'))
        return forbidden_cards


    def __start_play(self, room_jid, game_data, profile):
        """Start the game (tell to the first player after dealer to play"""
        game_data['stage'] = "play"
        next_player_idx = game_data['current_player'] = (game_data['init_player'] + 1) % len(game_data['players']) #the player after the dealer start
        game_data['first_player'] = next_player = game_data['players'][next_player_idx]
        to_jid = jid.JID(room_jid.userhost()+"/"+next_player) #FIXME: gof:
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
            self.createGame(_room_jid.userhost(), players, profile_key=profile)
        return True

    def launchGame(self, players, profile_key='@NONE@'):
        """Launch a game: helper method to create a room, invite players, and create the tarot game
        @param players: list for players jid"""
        debug(_('Launching tarot game'))
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            error(_("Unknown profile"))
            return

        def tarotRoomJoined(room):
            _room = room.occupantJID.userhostJID()
            for player in players:
                self.host.plugins["XEP-0249"].invite(jid.JID(player), room.occupantJID.userhostJID(), {"game":"Tarot"}, profile)
            self.waiting_inv[_room] = (time(), players) #TODO: remove invitation waiting for too long, using the time data
        
        def after_init(ignore):
            room_name = "sat_tarot_%s" % self.host.plugins["XEP-0045"].getUniqueName(profile_key)
            print "\n\n===> room_name:", room_name
            #muc_service = self.host.memory.getServerServiceEntity("conference", "text", profile)
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
            d = self.host.plugins["XEP-0045"].join(jid.JID("%s@%s" % (room_name, muc_service.userhost())), _jid.user, {}, profile).addCallback(tarotRoomJoined)

        client = self.host.getClient(profile)
        if not client:
            error(_('No client for this profile key: %s') % profile_key)
            return
        client.client_initialized.addCallback(after_init)




    def createGame(self, room_jid_param, players, profile_key='@NONE@'):
        """Create a new game
        @param room_jid_param: jid of the room
        @param players: list of players nick (nick must exist in the room)
        @param profile_key: %(doc_profile_key)s"""
        debug (_("Creating Tarot game"))
        room_jid = jid.JID(room_jid_param)
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            error (_("profile %s is unknown") % profile_key)
            return
        if self.games.has_key(room_jid):
            warning (_("Tarot game already started in room %s") % room_jid.userhost())
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
            self.games[room_jid.userhost()] = {'referee':referee, 'players':players, 'status':status, 'players_data':players_data, 'hand_size':18, 'init_player':0, 'current_player': None, 'contrat': None, 'stage': None}
            for player in players:
                mess = self.createGameElt(jid.JID(room_jid.userhost()+'/'+player))
                mess.firstChildElement().addChild(self.__create_started_elt(players))
                self.host.profiles[profile].xmlstream.send(mess)

    def newPlayerReady(self, player, referee, profile_key='@NONE@'):
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

    def contratChoosed(self, player, referee, contrat, profile_key='@NONE@'):
        """Must be call by player when the contrat is selected
        @param player: player's name
        @param referee: arbiter jid
        @contrat: contrat choosed (must be the exact same string than in the give list options)
        @profile_key: profile
        """
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            error (_("profile %s is unknown") % profile_key)
            return
        debug (_('contrat [%(contrat)s] choosed by %(profile)s') % {'contrat':contrat, 'profile':profile})
        mess = self.createGameElt(jid.JID(referee))
        contrat_elt = mess.firstChildElement().addElement(('','contrat_choosed'), content=contrat)
        contrat_elt['player'] = player
        self.host.profiles[profile].xmlstream.send(mess)

    def play_cards(self, player, referee, cards, profile_key='@NONE@'):
        """Must be call by player when the contrat is selected
        @param player: player's name
        @param referee: arbiter jid
        @cards: cards played (list of tuples)
        @profile_key: profile
        """
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            error (_("profile %s is unknown") % profile_key)
            return
        debug (_('Cards played by %(profile)s: [%(cards)s]') % {'profile':profile,'cards':cards})
        mess = self.createGameElt(jid.JID(referee))
        playcard_elt = mess.firstChildElement().addChild(self.__card_list_to_xml(TarotCard.from_tuples(cards), 'cards_played'))
        playcard_elt['player'] = player
        self.host.profiles[profile].xmlstream.send(mess)

    def newGame(self, room_jid, profile):
        """Launch a new round"""
        debug (_('new Tarot game'))
        deck = self.deck_ordered[:]
        random.shuffle(deck)
        game_data = self.games[room_jid.userhost()]
        players = game_data['players']
        players_data = game_data['players_data']
        current_player = game_data['current_player']
        game_data['stage'] = "init"
        game_data['first_player'] = None #first player for the current trick
        game_data['contrat'] = None
        hand = game_data['hand'] = {}
        hand_size = game_data['hand_size']
        chien = game_data['chien'] = []
        for i in range(4):
            hand[players[i]] = deck[0:hand_size]
            del deck[0:hand_size]
        chien.extend(deck)
        del(deck[:])

        for player in players:
            to_jid = jid.JID(room_jid.userhost()+"/"+player) #FIXME: gof:
            mess = self.createGameElt(to_jid)
            mess.firstChildElement().addChild(self.__card_list_to_xml(hand[player], 'hand'))
            self.host.profiles[profile].xmlstream.send(mess)
            players_data[player]['contrat'] = None
            players_data[player]['levees'] = [] #cards won
            players_data[player]['played'] = None #card on the table
            players_data[player]['wait_for_low'] = None #Used when a player wait for a low card because of excuse

        pl_idx = game_data['current_player'] = (game_data['init_player'] + 1) % len(players) #the player after the dealer start
        player = players[pl_idx]
        to_jid = jid.JID(room_jid.userhost()+"/"+player) #FIXME: gof:
        mess = self.createGameElt(to_jid)
        mess.firstChildElement().addChild(self.__ask_contrat())
        self.host.profiles[profile].xmlstream.send(mess)
            

    def card_game_cmd(self, mess_elt, profile):
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
                self.host.bridge.tarotGameStarted(room_jid.userhost(), from_jid.full(), players, profile)
            
            elif elt.name == 'player_ready': #ready to play
                player = elt['player']
                status = self.games[room_jid.userhost()]['status']
                nb_players = len(self.games[room_jid.userhost()]['players'])
                status[player] = 'ready'
                debug (_('Player %(player)s is ready to start [status: %(status)s]') % {'player':player, 'status':status})
                if status.values().count('ready') == nb_players: #everybody is ready, we can start the game
                    self.newGame(room_jid, profile)
            
            elif elt.name == 'hand': #a new hand has been received
                self.host.bridge.tarotGameNew(room_jid.userhost(), self.__xml_to_list(elt), profile)

            elif elt.name == 'contrat': #it's time to choose contrat
                form = data_form.Form.fromElement(elt.firstChildElement())
                xml_data = dataForm2xml(form)
                self.host.bridge.tarotGameChooseContrat(room_jid.userhost(), xml_data, profile)
           
            elif elt.name == 'contrat_choosed':
                #TODO: check we receive the contrat from the right person
                #TODO: use proper XEP-0004 way for answering form
                player = elt['player']
                players_data[player]['contrat'] = unicode(elt)
                contrats = [players_data[player]['contrat'] for player in game_data['players']]
                if contrats.count(None):
                    #not everybody has choosed his contrat, it's next one turn
                    player = self.__next_player(game_data)
                    to_jid = jid.JID(room_jid.userhost()+"/"+player) #FIXME: gof:
                    mess = self.createGameElt(to_jid)
                    mess.firstChildElement().addChild(self.__ask_contrat())
                    self.host.profiles[profile].xmlstream.send(mess)
                else:
                    best_contrat = [None, "Passe"]
                    for player in game_data['players']:
                        contrat = players_data[player]['contrat']
                        idx_best = self.contrats.index(best_contrat[1])
                        idx_pl = self.contrats.index(contrat)
                        if idx_pl > idx_best:
                            best_contrat[0] = player
                            best_contrat[1] = contrat
                    if best_contrat[1] == "Passe":
                        debug(_("Everybody is passing, round ended"))
                        to_jid = jid.JID(room_jid.userhost())
                        mess = self.createGameElt(to_jid)
                        mess.firstChildElement().addChild(self.__give_scores(*self.__draw_game(game_data)))
                        self.host.profiles[profile].xmlstream.send(mess)
                        game_data['init_player'] = (game_data['init_player'] + 1) % len(game_data['players']) #we change the dealer
                        for player in game_data['players']:
                            game_data['status'][player] = "init"
                        return
                    debug (_("%(player)s win the bid with %(contrat)s") % {'player':best_contrat[0],'contrat':best_contrat[1]})
                    game_data['contrat'] = best_contrat[1]
                    
                    if game_data['contrat'] == "Garde Sans" or game_data['contrat'] == "Garde Contre":
                        self.__start_play(room_jid, game_data, profile)
                        game_data['attaquant'] = best_contrat[0]
                    else:
                        #Time to show the chien to everybody
                        to_jid = jid.JID(room_jid.userhost()) #FIXME: gof:
                        mess = self.createGameElt(to_jid)
                        chien_elt = mess.firstChildElement().addChild(self.__card_list_to_xml(game_data['chien'], 'chien'))
                        chien_elt['attaquant'] = best_contrat[0]
                        self.host.profiles[profile].xmlstream.send(mess)
                        #the attacker (attaquant) get the chien
                        game_data['hand'][best_contrat[0]].extend(game_data['chien'])
                        del game_data['chien'][:]
                    
                    if game_data['contrat'] == "Garde Sans":
                        #The chien go into attaquant's (attacker) levees
                        players_data[best_contrat[0]]['levees'].extend(game_data['chien'])
                        del game_data['chien'][:]


            elif elt.name == 'chien': #we have received the chien
                debug (_("tarot: chien received"))
                data = {"attaquant":elt['attaquant']}
                game_data['stage'] = "ecart"
                game_data['attaquant'] = elt['attaquant']
                self.host.bridge.tarotGameShowCards(room_jid.userhost(), "chien", self.__xml_to_list(elt), data, profile)

            elif elt.name == 'cards_played':
                if game_data['stage'] == "ecart":
                    #TODO: show atouts (trumps) if player put some in écart
                    assert (game_data['attaquant'] == elt['player']) #TODO: throw an xml error here
                    list_cards = TarotCard.from_tuples(self.__xml_to_list(elt))
                    #we now check validity of card
                    invalid_cards = self.__invalid_cards(game_data, list_cards)
                    if invalid_cards:
                        mess = self.createGameElt(jid.JID(room_jid.userhost()+'/'+elt['player']))
                        mess.firstChildElement().addChild(self.__invalid_cards_elt(list_cards, invalid_cards, game_data['stage']))
                        self.host.profiles[profile].xmlstream.send(mess)
                        return

                    #FIXME: gof: manage Garde Sans & Garde Contre cases
                    players_data[elt['player']]['levees'].extend(list_cards) #we add the chien to attaquant's levées
                    for card in list_cards:
                        game_data['hand'][elt['player']].remove(card)
                    
                    self.__start_play(room_jid, game_data, profile)
                    
                elif game_data['stage'] == "play":
                    current_player = game_data['players'][game_data['current_player']]
                    cards = TarotCard.from_tuples(self.__xml_to_list(elt))
                    
                    if mess_elt['type'] == 'groupchat':
                        self.host.bridge.tarotGameCardsPlayed(room_jid.userhost(), elt['player'], self.__xml_to_list(elt), profile)
                    else:
                        #we first check validity of card
                        invalid_cards = self.__invalid_cards(game_data, cards)
                        if invalid_cards:
                            mess = self.createGameElt(jid.JID(room_jid.userhost()+'/'+current_player))
                            mess.firstChildElement().addChild(self.__invalid_cards_elt(cards, invalid_cards, game_data['stage']))
                            self.host.profiles[profile].xmlstream.send(mess)
                            return
                        #the card played is ok, we forward it to everybody
                        #first we remove it from the hand and put in on the table
                        game_data['hand'][current_player].remove(cards[0])
                        players_data[current_player]['played'] = cards[0]

                        #then we forward the message
                        mess = self.createGameElt(room_jid)
                        playcard_elt = mess.firstChildElement().addChild(elt)
                        self.host.profiles[profile].xmlstream.send(mess)
                    
                        #Did everybody played ?
                        played = [players_data[player]['played'] for player in game_data['players']]
                        if all(played):
                            #everybody has played
                            winner = self.__winner(game_data)
                            debug (_('The winner of this trick is %s') % winner)
                            #the winner win the trick
                            self.__excuse_hack(game_data, played, winner)
                            players_data[elt['player']]['levees'].extend(played)
                            #nothing left on the table
                            for player in game_data['players']:
                                players_data[player]['played'] = None
                            if len(game_data['hand'][current_player]) == 0:
                                #no card lef: the game is finished
                                to_jid = room_jid
                                mess = self.createGameElt(to_jid)
                                chien_elt = mess.firstChildElement().addChild(self.__give_scores(*self.__calculate_scores(game_data)))
                                self.host.profiles[profile].xmlstream.send(mess)
                                game_data['init_player'] = (game_data['init_player'] + 1) % len(game_data['players']) #we change the dealer
                                for player in game_data['players']:
                                    game_data['status'][player] = "init"
                                return
                            #next player is the winner
                            next_player = game_data['first_player'] = self.__next_player(game_data, winner)
                        else:
                            next_player = self.__next_player(game_data)

                        #finally, we tell to the next player to play
                        to_jid = jid.JID(room_jid.userhost()+"/"+next_player)
                        mess = self.createGameElt(to_jid)
                        yourturn_elt = mess.firstChildElement().addElement('your_turn')
                        self.host.profiles[profile].xmlstream.send(mess)

            elif elt.name == 'your_turn':
                self.host.bridge.tarotGameYourTurn(room_jid.userhost(), profile)

            elif elt.name == 'score':
                form_elt = elt.elements(name='x',uri='jabber:x:data').next()
                winners = []
                loosers = []
                for winner in elt.elements(name='winner', uri=NS_CG):
                    winners.append(unicode(winner))
                for looser in elt.elements(name='looser', uri=NS_CG):
                    loosers.append(unicode(looser))
                form = data_form.Form.fromElement(form_elt)
                xml_data = dataForm2xml(form)
                self.host.bridge.tarotGameScore(room_jid.userhost(), xml_data, winners, loosers, profile)
            elif elt.name == 'error':
                if elt['type'] == 'invalid_cards':
                    played_cards = self.__xml_to_list(elt.elements(name='played',uri=NS_CG).next())
                    invalid_cards = self.__xml_to_list(elt.elements(name='invalid',uri=NS_CG).next())
                    self.host.bridge.tarotGameInvalidCards(room_jid.userhost(), elt['phase'], played_cards, invalid_cards, profile)
                else:
                    error (_('Unmanaged error type: %s') % elt['type'])
            else:
                error (_('Unmanaged card game element: %s') % elt.name)
                
    def getHandler(self, profile):
            return CardGameHandler(self)

class CardGameHandler (XMPPHandler):
    implements(iwokkel.IDisco)
   
    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host

    def connectionInitialized(self):
        self.xmlstream.addObserver(CG_REQUEST, self.plugin_parent.card_game_cmd, profile = self.parent.profile)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=''):
        return [disco.DiscoFeature(NS_CG)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=''):
        return []

