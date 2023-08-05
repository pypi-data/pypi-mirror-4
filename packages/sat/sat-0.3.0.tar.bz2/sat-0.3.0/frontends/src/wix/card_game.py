#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
wix: a SAT frontend
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



import wx
import os.path, glob
import pdb
from logging import debug, info, error
from sat.tools.jid  import JID
from sat.tools.games import TarotCard
from sat_frontends.quick_frontend.quick_card_game import QuickCardGame
from sat_frontends.wix.xmlui import XMLUI

CARD_WIDTH = 74
CARD_HEIGHT = 136
MIN_WIDTH = 950 #Minimum size of the panel
MIN_HEIGHT = 500

class WxCard(TarotCard):
    """This class is used to represent a card, graphically and logically"""

    def __init__(self, file):
        """@param file: path of the PNG file"""
        self.bitmap = wx.Image(file).ConvertToBitmap()
        root_name = os.path.splitext(os.path.basename(file))[0]
        suit,value = root_name.split('_')
        TarotCard.__init__(self, (suit, value))
        print "Carte:",suit, value #, self.bout

    def draw(self, dc, x, y):
        """Draw the card on the device context
        @param dc: device context
        @param x: abscissa 
        @param y: ordinate"""
        dc.DrawBitmap(self.bitmap, x, y, True)


class CardPanel(QuickCardGame,wx.Panel):
    """This class is used to display the cards"""

    def __init__(self, parent, referee, players, player_nick):
        QuickCardGame.__init__(self, parent, referee, players, player_nick)
        wx.Panel.__init__(self, parent)
        self.SetMinSize(wx.Size(MIN_WIDTH, MIN_HEIGHT))
        self.loadCards(os.path.join(self.parent.host.media_dir, 'games/cards/tarot'))
        self.mouse_over_card = None #contain the card to highlight
        self.visible_size = CARD_WIDTH/2 #number of pixels visible for cards
        self.hand = []
        self.to_show = []
        self.state = None
        self.SetBackgroundColour(wx.GREEN)
        self.Bind(wx.EVT_SIZE, self.onResize)
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_MOTION, self.onMouseMove)
        self.Bind(wx.EVT_LEFT_UP, self.onMouseClick)
        self.parent.host.bridge.tarotGameReady(player_nick, referee, profile_key = self.parent.host.profile)

    def loadCards(self, dir):
        """Load all the cards in memory
        @param dir: directory where the PNG files are"""
        QuickCardGame.loadCards(self)
        for file in glob.glob(dir+'/*_*.png'):
            card = WxCard(file)
            self.cards[card.suit, card.value]=card
            self.deck.append(card)

    def newGame(self, hand):
        """Start a new game, with given hand"""
        QuickCardGame.newGame(self, hand)
        self._recalc_ori()
        self.Refresh()

    def contratSelected(self, data):
        """Called when the contrat has been choosed
        @param data: form result"""
        debug (_("Contrat choosed"))
        contrat = data[0][1]
        QuickCardGame.contratSelected(self, contrat)

    def chooseContrat(self, xml_data):
        """Called when the player as to select his contrat
        @param xml_data: SàT xml representation of the form"""
        misc = {'callback': self.contratSelected}
        form = XMLUI(self.parent.host, xml_data, title = _('Please choose your contrat'), options = ['NO_CANCEL'], misc = misc)

    def showScores(self, xml_data, winners, loosers):
        """Called when the player as to select hist contrat
        @param xml_data: SàT xml representation of the form"""
        def _new_game(ignore):
            self.resetRound()
            self.Refresh()
            self.parent.host.bridge.tarotGameReady(self.player_nick, self.referee, profile_key = self.parent.host.profile)

        if not winners and not loosers:
            title = _("Draw game")
        else:
            title = _('You win \o/') if self.player_nick in winners else _('You loose :(')
        form = XMLUI(self.parent.host, xml_data, title = title, options = ['NO_CANCEL'], misc={'callback':_new_game})

    def cardsPlayed(self, player, cards):
        """A card has been played by player"""
        QuickCardGame.cardsPlayed(self, player, cards)
        self.Refresh()

    def invalidCards(self, phase, played_cards, invalid_cards):
        """Invalid cards have been played
        @param phase: phase of the game
        @param played_cards: all the cards played
        @param invalid_cards: cards which are invalid"""
        QuickCardGame.invalidCards(self, phase, played_cards, invalid_cards)

        self._recalc_ori()
        self.Refresh()
        if self._autoplay==None: #No dialog if there is autoplay
            wx.MessageDialog(self, _("Cards played are invalid !"), _("Error"), wx.OK | wx.ICON_ERROR).ShowModal()

    def _is_on_hand(self, pos_x, pos_y):
        """Return True if the coordinate are on the hand cards"""
        if pos_x > self.orig_x and pos_y > self.orig_y \
           and pos_x < self.orig_x + (len(self.hand)+1) * self.visible_size \
           and pos_y < self.end_y:
           return True
        return False

    def onResize(self, event):
        self._recalc_ori()

    def _recalc_ori(self):
        """Recalculate origins of hand, must be call when hand size change"""
        self.orig_x = (self.GetSizeTuple()[0]-(len(self.hand)+1)*self.visible_size)/2 #where we start to draw cards
        self.orig_y = self.GetSizeTuple()[1] - CARD_HEIGHT - 20
        self.end_y = self.orig_y + CARD_HEIGHT

    def onPaint(self, event):
        dc = wx.PaintDC(self)
        
        #We print the names to know who play where TODO: print avatars when available
        max_x, max_y = self.GetSize()
        border = 10 #border between nick and end of panel
        right_y = left_y = 200
        right_width, right_height = dc.GetTextExtent(self.right_nick)
        right_x = max_x - right_width - border
        left_x = border
        top_width, top_height = dc.GetTextExtent(self.top_nick)
        top_x = (max_x - top_width) / 2
        top_y = border
        dc.DrawText(self.right_nick, right_x, right_y)
        dc.DrawText(self.top_nick, top_x, top_y)
        dc.DrawText(self.left_nick, left_x, left_y)

        #We draw the played cards:
        center_y = 200 #ordinate used as center point
        left_x = (max_x - CARD_WIDTH)/2 - CARD_WIDTH - 5
        right_x = (max_x/2) + (CARD_WIDTH/2) + 5
        left_y = right_y = center_y - CARD_HEIGHT/2
        top_x = bottom_x = (max_x - CARD_WIDTH)/2
        top_y = center_y - CARD_HEIGHT - 5
        bottom_y = center_y + 5
        for side in ['left', 'top', 'right', 'bottom']:
            card = self.played[getattr(self, side+'_nick')]
            if card != None:
                card.draw(dc,locals()[side+'_x'], locals()[side+'_y'])

        x=self.orig_x
        for card in self.hand:
            if (self.state == "play" or self.state == "ecart") and card == self.mouse_over_card \
                or self.state == "ecart" and card in self.selected:
                y = self.orig_y - 30
            else:
                y = self.orig_y

            card.draw(dc,x,y)
            x+=self.visible_size

        if self.to_show:
            """There are cards to display in the middle"""
            size = len(self.to_show)*(CARD_WIDTH+10)-10
            x = (max_x - size)/2
            for card in self.to_show:
                card.draw(dc, x, 150)
                x+=CARD_WIDTH+10

    def onMouseMove(self, event):
        pos_x,pos_y = event.GetPosition()
        if self._is_on_hand(pos_x, pos_y):
           try:
               self.mouse_over_card = self.hand[(pos_x-self.orig_x)/self.visible_size]
           except IndexError:
               self.mouse_over_card = self.hand[-1]
           self.Refresh()
        else:
            self.mouse_over_card = None
            self.Refresh()

    def onMouseClick(self, event):
        print "mouse click:",event.GetPosition()
        pos_x,pos_y = event.GetPosition()
        
        if self.state == "chien":
            self.to_show = []
            self.state = "wait"
            return
        elif self.state == "wait_for_ecart":
            self.state = "ecart"
            self.hand.extend(self.to_show)
            self.hand.sort()
            self.to_show = []
            self._recalc_ori()
            self.Refresh()
            return

        if self._is_on_hand(pos_x, pos_y):
           idx = (pos_x-self.orig_x)/self.visible_size
           if idx == len(self.hand):
               idx-=1
           if self.hand[idx] == self.mouse_over_card:
               if self.state == "ecart":
                   if self.hand[idx] in self.selected:
                       self.selected.remove(self.hand[idx])
                   else:
                       self.selected.append(self.hand[idx])
                       if len(self.selected) == 6: #TODO: use variable here, as chien len can change with variants
                           dlg = wx.MessageDialog(self, _("Do you put these cards in chien ?"), _(u"Écart"), wx.YES_NO | wx.ICON_QUESTION)
                           answer = dlg.ShowModal()
                           if answer == wx.ID_YES:
                               ecart = []
                               for card in self.selected:
                                   ecart.append((card.suit, card.value))
                                   self.hand.remove(card)
                               del self.selected[:]
                               self.parent.host.bridge.tarotGamePlayCards(self.player_nick, self.referee, ecart, profile_key = self.parent.host.profile)
                               self.state = "wait"

                   self._recalc_ori()
                   self.Refresh()
               if self.state == "play":
                   card = self.hand[idx]
                   self.parent.host.bridge.tarotGamePlayCards(self.player_nick, self.referee, [(card.suit, card.value)], profile_key = self.parent.host.profile)
                   del self.hand[idx]
                   self.state = "wait"
                   self._recalc_ori()
                   self.Refresh()


