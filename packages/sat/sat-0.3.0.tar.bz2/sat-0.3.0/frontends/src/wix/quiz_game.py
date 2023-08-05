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
from time import time
from math import sin, cos, pi

CARD_WIDTH = 74
CARD_HEIGHT = 136
WIDTH = 800
HEIGHT = 600

class GraphicElement():
    """This class is used to represent a card, graphically and logically"""

    def __init__(self, file, x=0, y=0, zindex=10, transparent=True):
        """ Image used to build the game visual
        @param file: path of the PNG file
        @param zindex: layer of the element (0=background; the bigger, the more in the foreground)"""
        self.bitmap = wx.Image(file).ConvertToBitmap()
        self.x = x
        self.y = y
        self.zindex = zindex
        self.transparent = transparent

    def __cmp__(self, other):
        return self.zindex.__cmp__(other.zindex)
    
    def draw(self, dc, x=None, y=None):
        """Draw the card on the device context
        @param dc: device context
        @param x: abscissa 
        @param y: ordinate"""
        dc.DrawBitmap(self.bitmap, x or self.x, y or self.y, self.transparent)

class BaseWindow(wx.Window):
    """This is the panel where the game is drawed, under the other widgets"""
    
    def __init__(self, parent):
        wx.Window.__init__(self, parent, pos=(0,0), size=(WIDTH, HEIGHT))
        self.parent = parent
        self.SetMinSize(wx.Size(WIDTH, HEIGHT))
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.graphic_elts = {}
        self.loadImages(os.path.join(parent.parent.host.media_dir, 'games/quiz/'))

    def loadImages(self, dir):
        """Load all the images needed for the game
        @param dir: directory where the PNG files are"""
        x_player = 24
        for name, sub_dir, filename, x, y, zindex, transparent in [("background", "background", "blue_background.png", 0, 0, 0, False),
                                                             ("joueur0", "characters", "zombie.png", x_player+0*184, 170, 5, True),
                                                             ("joueur1", "characters", "nerd.png", x_player+1*184, 170, 5, True),
                                                             ("joueur2", "characters", "zombie.png", x_player+2*184, 170, 5, True),
                                                             ("joueur3", "characters", "zombie.png", x_player+3*184, 170, 5, True),
                                                             ("foreground", "foreground", "foreground.png", 0, 0, 10, True)]:
            self.graphic_elts[name] = GraphicElement(os.path.join(dir, sub_dir, filename), x = x, y = y, zindex=zindex, transparent=transparent)

        self.right_image = wx.Image(os.path.join(dir, "foreground", "right.png")).ConvertToBitmap()
        self.wrong_image = wx.Image(os.path.join(dir, "foreground", "wrong.png")).ConvertToBitmap()

    def fullPaint(self, device_context):
        """Paint all the game on the given dc
        @param device_context: wx.DC"""
        elements = self.graphic_elts.values()
        elements.sort()
        for elem in elements:
            elem.draw(device_context)

        _font = wx.Font(65, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        device_context.SetFont(_font)
        device_context.SetTextForeground(wx.BLACK)

        for i in range(4):
            answer = self.parent.players_data[i]["answer"]
            score = self.parent.players_data[i]["score"]
            if answer == None:    
                device_context.DrawText("%d" % score, 100 + i*184, 355)
            else:
                device_context.DrawBitmap(self.right_image if answer else self.wrong_image, 39+i*184, 348, True)


        if self.parent.time_origin:
            device_context.SetPen(wx.BLACK_PEN)
            radius = 20
            center_x = 760
            center_y = 147
            origin = self.parent.time_origin
            current = self.parent.time_pause or time()
            limit = self.parent.time_limit
            total = limit - origin
            left = self.parent.time_left = max(0,limit - current)
            device_context.SetBrush(wx.RED_BRUSH if left/total < 1/4.0 else wx.WHITE_BRUSH)
            if left:
                #we now draw the timer
                angle = ((-2*pi)*((total-left)/total) + (pi/2))
                x = center_x + radius * cos(angle) 
                y = center_y - radius * sin(angle)
                device_context.DrawArc(center_x, center_y-radius, x, y, center_x, center_y)

    def onPaint(self, event):
        dc = wx.PaintDC(self)
        self.fullPaint(dc)
       


class QuizPanel(wx.Panel):
    """This class is used to display the quiz game"""

    def __init__(self, parent, referee, players, player_nick):
        wx.Panel.__init__(self, parent)
        self.referee = referee
        self.player_nick = player_nick
        self.players = players
        self.time_origin = None #set to unix time when the timer start
        self.time_limit = None
        self.time_left = None
        self.time_pause = None
        self.last_answer = None
        self.parent = parent
        self.SetMinSize(wx.Size(WIDTH, HEIGHT))
        self.SetSize(wx.Size(WIDTH, HEIGHT))
        self.base = BaseWindow(self)
        self.question = wx.TextCtrl(self, -1, pos=(168,17), size=(613, 94), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.answer = wx.TextCtrl(self, -1, pos=(410,569), size=(342, 21), style=wx.TE_PROCESS_ENTER)
        self.players_data = [{}, {}, {}, {}]
        for i in range(4):
            self.players_data[i]['bubble'] = wx.TextCtrl(self, -1, pos=(39+i*184, 120), size=(180, 56), style=wx.TE_MULTILINE | wx.TE_READONLY)
            self.players_data[i]['bubble'].Hide()
            self.players_data[i]['answer'] = None #True if the player gave a good answer
            self.players_data[i]['score'] = 0
        self.answer.Bind(wx.EVT_TEXT_ENTER, self.answered)
        self.parent.host.bridge.quizGameReady(player_nick, referee, profile_key = self.parent.host.profile)
        self.state = None
    
    def answered(self, event):
        """Called when the player gave an answer in the box"""
        self.last_answer = self.answer.GetValue()
        self.answer.Clear()
        if self.last_answer:
            self.parent.host.bridge.quizGameAnswer(self.player_nick, self.referee, self.last_answer, profile_key = self.parent.host.profile)

    def quizGameTimerExpired(self):
        """Called when nobody answered the question in time"""
        self.question.SetValue(_(u"Quel dommage, personne n'a trouvé la réponse\n\nAttention, la prochaine question arrive..."))

    def quizGameTimerRestarted(self, time_left):
        """Called when nobody answered the question in time"""
        timer_orig = self.time_limit - self.time_origin
        self.time_left = time_left
        self.time_limit = time() + time_left
        self.time_origin = self.time_limit - timer_orig
        self.time_pause = None
        self.__timer_refresh()

    def startTimer(self, timer=60):
        """Start the timer to answer the question"""
        self.time_left = timer
        self.time_origin = time()
        self.time_limit = self.time_origin + timer
        self.time_pause = None
        self.__timer_refresh()
        
    def __timer_refresh(self):
        self.Refresh()
        if self.time_left:
            wx.CallLater(1000, self.__timer_refresh)

    def quizGameNew(self, data):
        """Start a new game, with given hand"""
        if data.has_key('instructions'):
            self.question.ChangeValue(data['instructions'])
        self.Refresh()

    def quizGameQuestion(self, question_id, question, timer):
        """Called when a new question is available
        @param question: question to ask"""
        self.question.ChangeValue(question)
        self.startTimer(timer)
        self.last_answer = None
        self.answer.Clear()
    
    def quizGamePlayerBuzzed(self, player, pause):
        """Called when the player pushed the buzzer
        @param player: player who pushed the buzzer
        @param pause: should we stop the timer ?"""
        if pause:
            self.time_pause = time()
    
    def quizGamePlayerSays(self, player, text, delay):
        """Called when the player says something
        @param player: who is talking
        @param text: what the player says"""
        if player != self.player_nick and self.last_answer:
            #if we are not the player talking, and we have an answer, that mean that our answer has not been validated
            #we can put it again in the answering box
            self.answer.SetValue(self.last_answer)
        idx = self.players.index(player)
        bubble = self.players_data[idx]['bubble']
        bubble.SetValue(text)
        bubble.Show()
        self.Refresh()
        wx.CallLater(delay * 1000, bubble.Hide)

    def quizGameAnswerResult(self, player, good_answer, score):
        """Result of the just given answer
        @param player: who gave the answer
        @good_answer: True if the answer is right
        @score: dict of score"""
        player_idx = self.players.index(player)
        self.players_data[player_idx]['answer'] = good_answer
        for _player in score:
            _idx = self.players.index(_player)
            self.players_data[_idx]['score'] = score[_player]
        def removeAnswer():
            self.players_data[player_idx]['answer'] = None
            self.Refresh()
        wx.CallLater(2000, removeAnswer)
        self.Refresh()
