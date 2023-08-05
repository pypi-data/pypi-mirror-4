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

from logging import debug, info, error
from sat.tools.jid  import JID



class QuickCardGame():
    
    def __init__(self, parent, referee, players, player_nick):
        self._autoplay = None #XXX: use 0 to activate fake play, None else
        self.parent = parent
        self.referee = referee
        self.players = players
        self.played = {}
        for player in players:
            self.played[player] = None
        self.player_nick = player_nick
        self.bottom_nick = unicode(self.player_nick)
        idx = self.players.index(self.player_nick)
        idx = (idx + 1) % len(self.players)
        self.right_nick = unicode(self.players[idx])
        idx = (idx + 1) % len(self.players)
        self.top_nick = unicode(self.players[idx])
        idx = (idx + 1) % len(self.players)
        self.left_nick = unicode(self.players[idx])
        self.bottom_nick = unicode(player_nick)
        self.selected = [] #Card choosed by the player (e.g. during ecart)
        self.hand_size = 13 #number of cards in a hand
        self.hand = []
        self.to_show = []
        self.state = None

    def resetRound(self):
        """Reset the game's variables to be reatty to start the next round"""
        del self.selected[:]
        del self.hand[:]
        del self.to_show[:]
        self.state = None
        for pl in self.played:
            self.played[pl] = None
        
    def getPlayerLocation(self, nick):
        """return player location (top,bottom,left or right)"""
        for location in ['top','left','bottom','right']:
            if getattr(self,'%s_nick' % location) == nick:
                return location
        assert(False)

    def loadCards(self):
        """Load all the cards in memory
        @param dir: directory where the PNG files are"""
        self.cards={}
        self.deck=[]
        self.cards["atout"]={} #As Tarot is a french game, it's more handy & logical to keep french names
        self.cards["pique"]={} #spade
        self.cards["coeur"]={} #heart
        self.cards["carreau"]={} #diamond
        self.cards["trefle"]={} #club
    
    def newGame(self, hand):
        """Start a new game, with given hand"""
        assert (len(self.hand) == 0)
        for suit, value in hand:
            self.hand.append(self.cards[suit, value])
        self.hand.sort()
        self.state = "init"
    
    def contratSelected(self, contrat):
        """Called when the contrat has been choosed
        @param data: form result"""
        self.parent.host.bridge.tarotGameContratChoosed(self.player_nick, self.referee, contrat or 'Passe', self.parent.host.profile)

    def chooseContrat(self, xml_data):
        """Called when the player as to select his contrat
        @param xml_data: SàT xml representation of the form"""
        raise NotImplementedError
    
    def showCards(self, game_stage, cards, data):
        """Display cards in the middle of the game (to show for e.g. chien ou poignée)"""
        self.to_show = []
        for suit, value in cards:
            self.to_show.append(self.cards[suit, value])
        if game_stage == "chien" and data['attaquant'] == self.player_nick:
            self.state = "wait_for_ecart"
        else:
            self.state = "chien"

    def myTurn(self):
        """Called when we have to play :)"""
        if self.state == "chien":
            self.to_show = []
        self.state = "play"
        self.__fakePlay()
                  
    def __fakePlay(self):
        """Convenience method for stupid autoplay
        /!\ don't forgot to comment any interactive dialog for invalid card"""
        if self._autoplay == None:
            return
        if self._autoplay >= len(self.hand):
            self._autoplay = 0
        card = self.hand[self._autoplay]
        self.parent.host.bridge.tarotGamePlayCards(self.player_nick, self.referee, [(card.suit, card.value)], profile_key = self.parent.host.profile)
        del self.hand[self._autoplay]
        self.state = "wait"
        self._autoplay+=1

    def showScores(self, xml_data, winners, loosers):
        """Called at the end of a game
        @param xml_data: SàT xml representation of the scores
        @param winners: list of winners' nicks
        @param loosers: list of loosers' nicks"""
        raise NotImplementedError
    
    def cardsPlayed(self, player, cards):
        """A card has been played by player"""
        if self.to_show:
            self.to_show = []
        pl_cards = []
        if self.played[player] != None: #FIXME
            for pl in self.played:
                self.played[pl] = None
        for suit, value in cards:
            pl_cards.append(self.cards[suit, value])
        self.played[player] = pl_cards[0]
    
    def invalidCards(self, phase, played_cards, invalid_cards):
        """Invalid cards have been played
        @param phase: phase of the game
        @param played_cards: all the cards played
        @param invalid_cards: cards which are invalid"""

        if phase == "play":
            self.state = "play"
        elif phase == "ecart":
            self.state = "ecart"
        else:
            error ('INTERNAL ERROR: unmanaged game phase')
        
        for suit, value in played_cards:
            self.hand.append(self.cards[suit, value])
        
        self.hand.sort()
        self.__fakePlay()

