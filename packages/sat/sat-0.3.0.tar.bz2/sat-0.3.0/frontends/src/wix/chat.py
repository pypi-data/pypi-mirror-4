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
import os.path
import time
import pdb
from logging import debug, info, error, warning
from sat.tools.jid  import JID
from sat_frontends.quick_frontend.quick_chat import QuickChat
from sat_frontends.wix.contact_list import ContactList
from sat_frontends.wix.card_game import CardPanel
from sat_frontends.wix.quiz_game import QuizPanel


idSEND           = 1
idTAROT          = 2

class Chat(wx.Frame, QuickChat):
    """The chat Window for one to one conversations"""

    def __init__(self, target, host, type='one2one'):
        wx.Frame.__init__(self, None, title=target, pos=(0,0), size=(400,200))
        QuickChat.__init__(self, target, host, type) 

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        
        self.splitter = wx.SplitterWindow(self, -1)
        self.sizer.Add(self.splitter, 1, flag = wx.EXPAND)

        self.conv_panel = wx.Panel(self.splitter)
        self.conv_panel.sizer = wx.BoxSizer(wx.VERTICAL)
        self.subjectBox = wx.TextCtrl(self.conv_panel, -1, style = wx.TE_READONLY)
        self.chatWindow = wx.TextCtrl(self.conv_panel, -1, style = wx.TE_MULTILINE | wx.TE_RICH | wx.TE_READONLY)
        self.textBox = wx.TextCtrl(self.conv_panel, -1, style = wx.TE_PROCESS_ENTER)
        self.conv_panel.sizer.Add(self.subjectBox, flag=wx.EXPAND)
        self.conv_panel.sizer.Add(self.chatWindow, 1, flag=wx.EXPAND)
        self.conv_panel.sizer.Add(self.textBox, 0, flag=wx.EXPAND)
        self.conv_panel.SetSizer(self.conv_panel.sizer)
        self.splitter.Initialize(self.conv_panel)
        self.SetMenuBar(wx.MenuBar())
        
        #events
        self.Bind(wx.EVT_CLOSE, self.onClose, self)
        self.Bind(wx.EVT_TEXT_ENTER, self.onEnterPressed, self.textBox)

        #fonts
        self.font={}
        self.font["points"] = self.chatWindow.GetFont().GetPointSize()
        self.font["family"] = self.chatWindow.GetFont().GetFamily()
        
        
        #misc
        self.day_change = time.strptime(time.strftime("%a %b %d 00:00:00  %Y")) #struct_time of day changing time
        self.setType(self.type)
        self.textBox.SetFocus()
        self.Hide() #We hide because of the show toggle
   
    def __createPresents(self):
        """Create a list of present people in a group chat"""
        self.present_panel = wx.Panel(self.splitter)
        self.present_panel.sizer = wx.BoxSizer(wx.VERTICAL)
        self.present_panel.presents = ContactList(self.present_panel, self.host, type='nicks')
        self.present_panel.presents.SetMinSize(wx.Size(80,20))
        self.present_panel.sizer.Add(self.present_panel.presents, 1, wx.EXPAND)
        self.present_panel.SetSizer(self.present_panel.sizer)
        self.splitter.SplitVertically(self.present_panel, self.conv_panel, 80)

    def setType(self, type):
        QuickChat.setType(self, type)
        if type is 'group' and not self.splitter.IsSplit():
            self.__createPresents()
            self.subjectBox.Show()
            self.__eraseMenus()
            self.__createMenus_group()
            self.sizer.Layout()
        elif type is 'one2one' and self.splitter.IsSplit():
            self.splitter.Unsplit(self.present_panel)
            del self.present_panel
            self.GetMenuBar().Show()
            self.subjectBox.Hide()
            self.__eraseMenus()
            self.__createMenus_O2O()
            self.nick = None
        else:
            self.subjectBox.Hide()
            self.__eraseMenus()
            self.__createMenus_O2O()
            self.historyPrint(profile=self.host.profile)
    
    def startGame(self, game_type, referee, players):
        """Configure the chat window to start a game"""
        if game_type=="Tarot":
            debug (_("configure chat window for Tarot game"))
            self.tarot_panel = CardPanel(self, referee, players, self.nick)
            self.sizer.Prepend(self.tarot_panel, 0, flag=wx.EXPAND)
            self.sizer.Layout()
            self.Fit()
            self.splitter.UpdateSize()
        elif game_type=="Quiz":
            debug (_("configure chat window for Quiz game"))
            self.quiz_panel = QuizPanel(self, referee, players, self.nick)
            self.sizer.Prepend(self.quiz_panel, 0, flag=wx.EXPAND)
            self.sizer.Layout()
            self.Fit()
            self.splitter.UpdateSize()

    def getGame(self, game_type):
        """Return class managing the game type"""
        #TODO: check that the game is launched, and manage errors
        if game_type=="Tarot":
            return self.tarot_panel 
        elif game_type=="Quiz":
            return self.quiz_panel 

    def setPresents(self, nicks):
        """Set the users presents in the contact list for a group chat
        @param nicks: list of nicknames
        """
        QuickChat.setPresents(self, nicks)
        for nick in nicks:
            self.present_panel.presents.replace(nick)
    
    def replaceUser(self, nick, show_info=True):
        """Add user if it is not in the group list"""
        debug (_("Replacing user %s") % nick)
        if self.type != "group":
            error (_("[INTERNAL] trying to replace user for a non group chat window"))
            return
        QuickChat.replaceUser(self, nick, show_info)
        self.present_panel.presents.replace(nick)

    def removeUser(self, nick, show_info=True):
        """Remove a user from the group list"""
        QuickChat.removeUser(self, nick, show_info)
        self.present_panel.presents.remove(nick)

    def setSubject(self, subject):
        """Set title for a group chat"""
        QuickChat.setSubject(self, subject)
        self.subjectBox.SetValue(subject)

    def __eraseMenus(self):
        """erase all menus"""
        menuBar = self.GetMenuBar()
        for i in range(menuBar.GetMenuCount()):
            menuBar.Remove(i)
    
    def __createMenus_O2O(self):
        """create menu bar for one 2 one chat"""
        info("Creating menus")
        self.__eraseMenus()
        menuBar = self.GetMenuBar()
        actionMenu = wx.Menu()
        actionMenu.Append(idSEND, _("&SendFile	CTRL-s"),_(" Send a file to contact"))
        menuBar.Append(actionMenu,_("&Action"))

        #events
        wx.EVT_MENU(self, idSEND, self.onSendFile)

    def __createMenus_group(self):
        """create menu bar for group chat"""
        info("Creating menus")
        self.__eraseMenus()
        menuBar = self.GetMenuBar()
        actionMenu = wx.Menu()
        actionMenu.Append(idTAROT, _("Start &Tarot game	CTRL-t"),_(" Start a Tarot card game")) #tmp
        menuBar.Append(actionMenu,_("&Games"))

        #events
        wx.EVT_MENU(self, idTAROT, self.onStartTarot)
    
    def __del__(self):
        wx.Frame.__del__(self)

    def onClose(self, event):
        """Close event: we only hide the frame."""
        event.Veto()
        self.Hide()

    def onEnterPressed(self, event):
        """Behaviour when enter pressed in send line."""
        self.host.sendMessage(self.target.short if self.type=='group' else self.target,
                                     event.GetString(), 
                                     mess_type = "groupchat" if self.type=='group' else "chat",
                                     profile_key=self.host.profile)
        self.textBox.Clear()

    def __blink(self):
        """Do wizzz and buzzz to show window to user or
        at least inform him of something new"""
        #TODO: use notification system
        if not self.IsActive():
            self.RequestUserAttention()
        if not self.IsShown():
            self.Show()

    def printMessage(self, from_jid, msg, profile, timestamp=""):
        """Print the message with differents colors depending on where it comes from."""
        try:
            jid,nick,mymess = QuickChat.printMessage(self, from_jid, msg, profile, timestamp)
        except TypeError:
            return
        print "printMessage, jid=",jid,"type=",self.type
        _font_bold = wx.Font(self.font["points"], self.font["family"], wx.NORMAL, wx.BOLD)
        _font_normal = wx.Font(self.font["points"], self.font["family"], wx.NORMAL, wx.NORMAL)
        _font_italic = wx.Font(self.font["points"], self.font["family"], wx.ITALIC if mymess else wx.NORMAL, wx.NORMAL)
        self.chatWindow.SetDefaultStyle(wx.TextAttr("GREY", font=_font_normal))
        msg_time = time.localtime(timestamp or None)
        time_format = "%c" if msg_time < self.day_change else "%H:%M" #if the message was sent before today, we print the full date
        self.chatWindow.AppendText("[%s]" % time.strftime(time_format, msg_time ))
        self.chatWindow.SetDefaultStyle(wx.TextAttr( "BLACK" if mymess else "BLUE", font=_font_bold))
        self.chatWindow.AppendText("[%s] " % nick)
        self.chatWindow.SetDefaultStyle(wx.TextAttr("BLACK", font=_font_italic))
        self.chatWindow.AppendText("%s\n" % msg)
        if not mymess:
            self.__blink()
    
    def printInfo(self, msg, type='normal'):
        """Print general info
        @param msg: message to print
        @type: one of:
            normal: general info like "toto has joined the room"
            me: "/me" information like "/me clenches his fist" ==> "toto clenches his fist"
        """
        _font_bold = wx.Font(self.font["points"], self.font["family"], wx.NORMAL, wx.BOLD)
        _font_normal = wx.Font(self.font["points"], self.font["family"], wx.NORMAL, wx.NORMAL)
        self.chatWindow.SetDefaultStyle(wx.TextAttr("BLACK", font=_font_bold if type == 'normal' else _font_normal))
        self.chatWindow.AppendText("%s\n" % msg)
        if type=="me":
            self.__blink()

    ### events ###

    def onSendFile(self, e):
        debug(_("Send File"))
        filename = wx.FileSelector(_("Choose a file to send"), flags = wx.FD_FILE_MUST_EXIST)
        if filename:
            debug(_("filename: %s"),filename)
            #FIXME: check last_resource: what if self.target.resource exists ?
            last_resource = self.host.bridge.getLastResource(unicode(self.target.short), self.host.profile)
            if last_resource:
                full_jid = JID("%s/%s" % (self.target.short, last_resource))
            else:
                full_jid = self.target
            id = self.host.bridge.sendFile(full_jid, filename, {}, self.host.profile)
            self.host.waitProgress(id, _("File Transfer"), _("Copying %s") % os.path.basename(filename), self.host.profile) 

    def onStartTarot(self, e):
        debug (_("Starting Tarot game"))
        warning (_("FIXME: temporary menu, must be changed"))
        if len(self.occupants) != 4:
            err_dlg = wx.MessageDialog(self, _("You need to be exactly 4 peoples in the room to start a Tarot game"), _("Can't start game"), style = wx.OK | wx.ICON_ERROR) #FIXME: gof: temporary only, need to choose the people with who the game has to be started
            err_dlg.ShowModal()
        else:
            self.host.bridge.tarotGameCreate(self.id, list(self.occupants), self.host.profile)
