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


from sat_frontends.quick_frontend.quick_chat_list import QuickChatList
from sat_frontends.quick_frontend.quick_app import QuickApp
import wx
from sat_frontends.wix.contact_list import ContactList
from sat_frontends.wix.chat import Chat
from sat_frontends.wix.param import Param
from sat_frontends.wix.xmlui import XMLUI
from sat_frontends.wix.gateways import GatewaysManager
from sat_frontends.wix.profile import Profile
from sat_frontends.wix.profile_manager import ProfileManager
import os.path
from sat.tools.jid  import JID
from logging import debug, info, warning, error
import sat_frontends.wix.constants

idCONNECT,\
idDISCONNECT,\
idEXIT,\
idABOUT,\
idPARAM,\
idADD_CONTACT,\
idREMOVE_CONTACT,\
idSHOW_PROFILE,\
idJOIN_ROOM,\
idFIND_GATEWAYS = range(10)

class ChatList(QuickChatList):
    """This class manage the list of chat windows"""
    
    def createChat(self, target):
        return Chat(target, self.host)
    
class MainWindow(wx.Frame, QuickApp):
    """main app window"""

    def __init__(self):
        QuickApp.__init__(self)
        wx.Frame.__init__(self,None, title="SàT Wix", size=(300,500))

        #sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        
        #Frame elements
        self.contact_list = ContactList(self, self)
        self.contact_list.registerActivatedCB(self.onContactActivated)
        self.contact_list.Hide()
        self.sizer.Add(self.contact_list, 1, flag=wx.EXPAND)
        
        self.chat_wins=ChatList(self)
        self.CreateStatusBar()

        #ToolBar
        self.tools=self.CreateToolBar()
        self.statusBox =  wx.ComboBox(self.tools, -1, "Online", choices=[status[1] for status in const_STATUS],
                                      style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.tools.AddControl(self.statusBox)
        self.tools.AddSeparator()
        self.statusTxt=wx.TextCtrl(self.tools, -1, style = wx.TE_PROCESS_ENTER)
        self.tools.AddControl(self.statusTxt)
        self.Bind(wx.EVT_COMBOBOX, self.onStatusChange, self.statusBox) 
        self.Bind(wx.EVT_TEXT_ENTER, self.onStatusChange, self.statusTxt)
        self.tools.Disable()

        
        
        #tray icon
        ticon = wx.Icon(os.path.join(self.media_dir, 'icons/crystal/tray_icon.xpm'), wx.BITMAP_TYPE_XPM)
        self.tray_icon = wx.TaskBarIcon()
        self.tray_icon.SetIcon(ticon, _("Wix jabber client"))
        wx.EVT_TASKBAR_LEFT_UP(self.tray_icon, self.onTrayClick)


        #events
        self.Bind(wx.EVT_CLOSE, self.onClose, self)
        
        #menus
        self.createMenus()
        for i in range(self.menuBar.GetMenuCount()):
            self.menuBar.EnableTop(i, False)
        
        #profile panel
        self.profile_pan = ProfileManager(self) 
        self.sizer.Add(self.profile_pan, 1, flag=wx.EXPAND)
      
        self.postInit()

        self.Show()

    def plug_profile(self, profile_key='@DEFAULT@'):
        """Hide profile panel then plug profile"""
        debug (_('plugin profile %s' % profile_key))
        self.profile_pan.Hide()
        self.contact_list.Show()
        self.sizer.Layout()
        for i in range(self.menuBar.GetMenuCount()):
            self.menuBar.EnableTop(i, True)
        super(MainWindow, self).plug_profile(profile_key)

    def createMenus(self):
        info(_("Creating menus"))
        connectMenu = wx.Menu()
        connectMenu.Append(idCONNECT, _("&Connect	CTRL-c"),_(" Connect to the server"))
        connectMenu.Append(idDISCONNECT, _("&Disconnect	CTRL-d"),_(" Disconnect from the server"))
        connectMenu.Append(idPARAM,_("&Parameters"),_(" Configure the program"))
        connectMenu.AppendSeparator()
        connectMenu.Append(idABOUT,_("A&bout"),_(" About %s") % APP_NAME)
        connectMenu.Append(idEXIT,_("E&xit"),_(" Terminate the program"))
        contactMenu = wx.Menu()
        contactMenu.Append(idADD_CONTACT, _("&Add contact"),_(" Add a contact to your list"))
        contactMenu.Append(idREMOVE_CONTACT, _("&Remove contact"),_(" Remove the selected contact from your list"))
        contactMenu.AppendSeparator()
        contactMenu.Append(idSHOW_PROFILE, _("&Show profile"), _(" Show contact's profile"))
        communicationMenu = wx.Menu()
        communicationMenu.Append(idJOIN_ROOM, _("&Join Room"),_(" Join a Multi-User Chat room"))
        communicationMenu.Append(idFIND_GATEWAYS, _("&Find Gateways"),_(" Find gateways to legacy IM"))
        self.menuBar = wx.MenuBar()
        self.menuBar.Append(connectMenu,_("&General"))
        self.menuBar.Append(contactMenu,_("&Contacts"))
        self.menuBar.Append(communicationMenu,_("&Communication"))
        self.SetMenuBar(self.menuBar)

        #additionals menus
        #FIXME: do this in a more generic way (in quickapp)
        add_menus = self.bridge.getMenus()
        for menu in add_menus:
            category,item,type = menu
            assert(type=="NORMAL") #TODO: manage other types
            menu_idx = self.menuBar.FindMenu(category)
            current_menu = None
            if menu_idx == wx.NOT_FOUND:
                #the menu is new, we create it
                current_menu = wx.Menu()
                self.menuBar.Append(current_menu, category)
            else:
                current_menu = self.menuBar.GetMenu(menu_idx)
            assert(current_menu != None)
            item_id = wx.NewId()
            help_string = self.bridge.getMenuHelp(category, item, type)
            current_menu.Append(item_id, item, help = help_string)
            #now we register the event
            def event_answer(e):
                id = self.bridge.callMenu(category, item, type, self.profile)
                self.current_action_ids.add(id)
            wx.EVT_MENU(self, item_id, event_answer)


        #events
        wx.EVT_MENU(self, idCONNECT, self.onConnectRequest)
        wx.EVT_MENU(self, idDISCONNECT, self.onDisconnectRequest)
        wx.EVT_MENU(self, idPARAM, self.onParam)
        wx.EVT_MENU(self, idABOUT, self.onAbout)
        wx.EVT_MENU(self, idEXIT, self.onExit)
        wx.EVT_MENU(self, idADD_CONTACT, self.onAddContact)
        wx.EVT_MENU(self, idREMOVE_CONTACT, self.onRemoveContact)
        wx.EVT_MENU(self, idSHOW_PROFILE, self.onShowProfile)
        wx.EVT_MENU(self, idJOIN_ROOM, self.onJoinRoom)
        wx.EVT_MENU(self, idFIND_GATEWAYS, self.onFindGateways)


    def newMessage(self, from_jid, to_jid, msg, _type, extra, profile):
        QuickApp.newMessage(self, from_jid, to_jid, msg, _type, extra, profile)

    def showAlert(self, message):
        # TODO: place this in a separate class
        popup=wx.PopupWindow(self)
        ### following code come from wxpython demo
        popup.SetBackgroundColour("CADET BLUE")
        st = wx.StaticText(popup, -1, message, pos=(10,10))
        sz = st.GetBestSize()
        popup.SetSize( (sz.width+20, sz.height+20) )
        x=(wx.DisplaySize()[0]-popup.GetSize()[0])/2
        popup.SetPosition((x,0))
        popup.Show()
        wx.CallLater(5000,popup.Destroy)
    
    def showDialog(self, message, title="", type="info", answer_cb = None, answer_data = None):
        if type == 'info':
            flags = wx.OK | wx.ICON_INFORMATION
        elif type == 'error':
            flags = wx.OK | wx.ICON_ERROR
        elif type == 'yes/no':
            flags = wx.YES_NO | wx.ICON_QUESTION
        else:
            flags = wx.OK | wx.ICON_INFORMATION
            error(_('unmanaged dialog type: %s'), type)
        dlg = wx.MessageDialog(self, message, title, flags)
        answer = dlg.ShowModal()
        dlg.Destroy()
        if answer_cb:
            data = [answer_data] if answer_data else []
            answer_cb(True if (answer == wx.ID_YES or answer == wx.ID_OK) else False, *data)
       
    def setStatusOnline(self, online=True):
        """enable/disable controls, must be called when local user online status change"""
        if online:
            self.SetStatusText(msgONLINE)
            self.tools.Enable()
        else:
            self.SetStatusText(msgOFFLINE)
            self.tools.Disable()
        return

    def askConfirmation(self, confirmation_id, confirmation_type, data, profile):
        #TODO: refactor this in QuickApp
        if not self.check_profile(profile):
            return
        debug (_("Confirmation asked"))
        answer_data={}
        if confirmation_type == "FILE_TRANSFER":
            debug (_("File transfer confirmation asked"))
            dlg = wx.MessageDialog(self, _("The contact %(jid)s wants to send you the file %(filename)s\nDo you accept ?") % {'jid':data["from"], 'filename':data["filename"]},
                                   _('File Request'),
                                   wx.YES_NO | wx.ICON_QUESTION
                                  )
            answer=dlg.ShowModal()
            if answer==wx.ID_YES:
                filename = wx.FileSelector(_("Where do you want to save the file ?"), flags = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
                if filename:
                    answer_data["dest_path"] = filename
                    self.bridge.confirmationAnswer(confirmation_id, True, answer_data, profile)
                    self.waitProgress(confirmation_id, _("File Transfer"), _("Copying %s") % os.path.basename(filename), profile) 
                else:
                    answer = wx.ID_NO
            if answer==wx.ID_NO:
                    self.bridge.confirmationAnswer(confirmation_id, False, answer_data, profile)
            
            dlg.Destroy()

        elif confirmation_type == "YES/NO":
            debug (_("Yes/No confirmation asked"))
            dlg = wx.MessageDialog(self, data["message"],
                                   _('Confirmation'),
                                   wx.YES_NO | wx.ICON_QUESTION
                                  )
            answer=dlg.ShowModal()
            if answer==wx.ID_YES:
                self.bridge.confirmationAnswer(confirmation_id, True, {}, profile)
            if answer==wx.ID_NO:
                self.bridge.confirmationAnswer(confirmation_id, False, {}, profile)

            dlg.Destroy()

    def actionResult(self, type, id, data, profile):
        if not self.check_profile(profile):
            return
        debug (_("actionResult: type = [%(type)s] id = [%(id)s] data = [%(data)s]") % {'type':type, 'id':id, 'data':data})
        if not id in self.current_action_ids:
            debug (_('unknown id, ignoring'))
            return
        if type == "SUPPRESS":
            self.current_action_ids.remove(id)
        elif type == "SUCCESS":
            self.current_action_ids.remove(id)
            dlg = wx.MessageDialog(self, data["message"],
                                   _('Success'),
                                   wx.OK | wx.ICON_INFORMATION
                                  )
            dlg.ShowModal()
            dlg.Destroy()
        elif type == "ERROR":
            self.current_action_ids.remove(id)
            dlg = wx.MessageDialog(self, data["message"],
                                   _('Error'),
                                   wx.OK | wx.ICON_ERROR
                                  )
            dlg.ShowModal()
            dlg.Destroy()
        elif type == "XMLUI":
            self.current_action_ids.remove(id)
            debug (_("XML user interface received"))
            misc = {}
            #FIXME FIXME FIXME: must clean all this crap !
            title = _('Form')
            if data['type'] == _('registration'):
                title = _('Registration')
                misc['target'] = data['target']
                misc['action_back'] = self.bridge.gatewayRegister
            XMLUI(self, title=title, xml_data = data['xml'], misc = misc)
        elif type == "RESULT":
            self.current_action_ids.remove(id)
            if self.current_action_ids_cb.has_key(id):
                callback = self.current_action_ids_cb[id]
                del self.current_action_ids_cb[id]
                callback(data)
        elif type == "DICT_DICT":
            self.current_action_ids.remove(id)
            if self.current_action_ids_cb.has_key(id):
                callback = self.current_action_ids_cb[id]
                del self.current_action_ids_cb[id]
                callback(data)
        else:
            error (_("FIXME FIXME FIXME: type [%s] not implemented") % type)
            raise NotImplementedError



    def progressCB(self, progress_id, title, message, profile):
        data = self.bridge.getProgress(progress_id, profile)
        if data:
            if not self.pbar:
                #first answer, we must construct the bar
                self.pbar = wx.ProgressDialog(title, message, float(data['size']), None,
                    wx.PD_SMOOTH | wx.PD_ELAPSED_TIME | wx.PD_ESTIMATED_TIME | wx.PD_REMAINING_TIME) 
                self.pbar.finish_value = float(data['size'])
                
            self.pbar.Update(int(data['position']))
        elif self.pbar:
            self.pbar.Update(self.pbar.finish_value)
            return

        wx.CallLater(10, self.progressCB, progress_id, title, message, profile)
        
    def waitProgress (self, progress_id, title, message, profile):
        self.pbar = None
        wx.CallLater(10, self.progressCB, progress_id, title, message, profile)
        
        

    ### events ###

    def onContactActivated(self, jid):
        debug (_("onContactActivated: %s"), jid)
        if self.chat_wins[jid.short].IsShown():
            self.chat_wins[jid.short].Hide()
        else:
            self.chat_wins[jid.short].Show()

    def onConnectRequest(self, e):
        self.bridge.connect(self.profile)

    def onDisconnectRequest(self, e):
        self.bridge.disconnect(self.profile)

    def __updateStatus(self):
        show = filter(lambda x:x[1] == self.statusBox.GetValue(), const_STATUS)[0][0]
        status =  self.statusTxt.GetValue()
        self.bridge.setPresence(show=show, statuses={'default':status}, profile_key=self.profile)  #FIXME: manage multilingual statuses

    def onStatusChange(self, e):
        debug(_("Status change request"))
        self.__updateStatus()

    def onParam(self, e):
        debug(_("Param request"))
        #xmlui = self.bridge.getParamsUI(self.profile)
        #XMLUI(self, xml_data = xmlui)
        param=Param(self)

    def onAbout(self, e):
        about = wx.AboutDialogInfo()
        about.SetName(APP_NAME)
        about.SetVersion (unicode(self.bridge.getVersion()))
        about.SetCopyright(u"(C) 2009, 2010, 2011, 2012, 2013 Jérôme Poisson aka Goffi")
        about.SetDescription( _(u"%(name)s is a SàT (Salut à Toi) frontend\n"+
        u"%(name)s is based on WxPython, and is the standard graphic interface of SàT") % {'name':APP_NAME})
        about.SetWebSite(("http://www.goffi.org", "Goffi's non-hebdo (french)"))
        about.SetDevelopers([ "Goffi (Jérôme Poisson)"])
        try:
            with open(LICENCE_PATH,"r") as licence:
                about.SetLicence(''.join(licence.readlines()))
        except:
            pass

        wx.AboutBox(about)

    def onExit(self, e):
        self.Close()
    
    def onAddContact(self, e):
        debug(_("Add contact request"))
        dlg = wx.TextEntryDialog(
                self, _('Please enter new contact JID'),
                _('Adding a contact'), _('name@server.tld'))

        if dlg.ShowModal() == wx.ID_OK:
            jid=JID(dlg.GetValue())
            if jid.is_valid():
                self.bridge.addContact(jid.short, profile_key=self.profile)
            else:
                error (_("'%s' is an invalid JID !"), jid)
                #TODO: notice the user

        dlg.Destroy()

    def onRemoveContact(self, e):
        debug(_("Remove contact request"))
        target = self.contact_list.getSelection()
        if not target:
            dlg = wx.MessageDialog(self, _("You haven't selected any contact !"),
                                   _('Error'),
                                   wx.OK | wx.ICON_ERROR
                                  )
            dlg.ShowModal()
            dlg.Destroy()
            return

        dlg = wx.MessageDialog(self, _("Are you sure you want to delete %s from your roster list ?") % target.short,
                               _('Contact suppression'),
                               wx.YES_NO | wx.ICON_QUESTION
                              )

        if dlg.ShowModal() == wx.ID_YES:
            info(_("Unsubscribing %s presence"), target.short)
            self.bridge.delContact(target.short, profile_key=self.profile)

        dlg.Destroy()

    def onShowProfile(self, e):
        debug(_("Show contact's profile request"))
        target = self.contact_list.getSelection()
        if not target:
            dlg = wx.MessageDialog(self, _("You haven't selected any contact !"),
                                   _('Error'),
                                   wx.OK | wx.ICON_ERROR
                                  )
            dlg.ShowModal()
            dlg.Destroy()
            return
        _id = self.bridge.getCard(target.short, profile_key=self.profile) 
        self.current_action_ids.add(_id)
        self.current_action_ids_cb[_id] = self.onProfileReceived
   
    def onProfileReceived(self, data):
        """Called when a profile is received"""
        debug (_('Profile received: [%s]') % data)
        profile=Profile(self, data)
        
    def onJoinRoom(self, e):
        warning('FIXME: temporary menu, must be improved')
        #TODO: a proper MUC room joining dialog with nickname etc
        dlg = wx.TextEntryDialog(
                self, _("Please enter MUC's JID"),
                #_('Entering a MUC room'), 'test@conference.necton2.int')
                _('Entering a MUC room'), 'room@muc_service.server.tld')
        if dlg.ShowModal() == wx.ID_OK:
            room_jid=JID(dlg.GetValue())
            if room_jid.is_valid():
                self.bridge.joinMUC(room_jid, self.profiles[self.profile]['whoami'].node, {}, self.profile)
            else:
                error (_("'%s' is an invalid JID !"), room_jid)

    def onFindGateways(self, e):
        debug(_("Find Gateways request"))
        _id = self.bridge.findGateways(self.profiles[self.profile]['whoami'].domain, self.profile)
        self.current_action_ids.add(_id)
        self.current_action_ids_cb[_id] = self.onGatewaysFound

    def onGatewaysFound(self, data):
        """Called when SàT has found the server gateways"""
        target = data['__private__']['target']
        del data['__private__']
        gatewayManager = GatewaysManager(self, data, server=target)
    
    def onClose(self, e):
        QuickApp.onExit(self)
        info(_("Exiting..."))
        for win in self.chat_wins:
            self.chat_wins[win].Destroy()
        e.Skip()

    def onTrayClick(self, e):
        debug(_("Tray Click"))
        if self.IsShown():
            self.Hide()
        else:
            self.Show()
            self.Raise()
        e.Skip()
    
