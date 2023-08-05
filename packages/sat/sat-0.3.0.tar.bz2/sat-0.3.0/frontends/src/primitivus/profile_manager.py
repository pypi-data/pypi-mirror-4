#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Primitivus: a SAT frontend
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

import urwid
from urwid_satext.sat_widgets import AdvancedEdit,Password,List,InputDialog,ConfirmDialog,Alert,FocusFrame
from sat.tools.jid import JID


class ProfileManager(urwid.WidgetWrap):

    def __init__(self, host):
        self.host = host
        #profiles list
        profiles = self.host.bridge.getProfilesList()
        profiles.sort()
        
        #login & password box must be created before list because of onProfileChange
        self.login_wid = AdvancedEdit(_('Login:'),align='center')
        self.pass_wid = Password(_('Password:'),align='center')
        
        self.list_profile = List(profiles, style=['single'], align='center', on_change=self.onProfileChange)

        #new & delete buttons
        buttons = [urwid.Button(_("New"), self.onNewProfile),
                  urwid.Button(_("Delete"), self.onDeleteProfile)]
        buttons_flow = urwid.GridFlow(buttons, max([len(button.get_label()) for button in buttons])+4, 1, 1, 'center')

        #second part: login information:
        divider = urwid.Divider('-')

        #connect button
        connect_button = urwid.Button(_("Connect"), self.onConnectProfile)

        #we now build the widget
        body_content = urwid.SimpleListWalker([buttons_flow,self.list_profile,divider,self.login_wid, self.pass_wid, connect_button])
        frame_body = urwid.ListBox(body_content)
        frame = urwid.Frame(frame_body,urwid.AttrMap(urwid.Text(_("Profile Manager"),align='center'),'title'))
        self.main_widget = urwid.LineBox(frame)
        urwid.WidgetWrap.__init__(self, self.main_widget)

    def __refillProfiles(self):
        """Update the list of profiles"""
        profiles = self.host.bridge.getProfilesList()
        profiles.sort()
        self.list_profile.changeValues(profiles)

    def cancelDialog(self, button):
        self.host.removePopUp()

    def newProfile(self, button, edit):
        """Create the profile"""
        name = edit.get_edit_text()
        self.host.bridge.asyncCreateProfile(name, callback=lambda: self._newProfileCreated(name), errback=self._profileCreationFailure)

    def _newProfileCreated(self, name):
        self.__refillProfiles()
        #We select the profile created in the list
        self.list_profile.selectValue(name)
        self.host.removePopUp()
        self.host.redraw()

    def _profileCreationFailure(self, reason):
        self.host.removePopUp()
        if reason=="CONFLICT":
            message=_("A profile with this name already exists")
        elif reason=="CANCELED":
            message=_("Profile creation cancelled by backend")
        elif reason=="DATABASE":
            message=_("Database error")
        else:
            message=_("Unknown reason (%s)") % reason
        popup = Alert(_("Can't create profile"), message, ok_cb=self.host.removePopUp)
        self.host.showPopUp(popup)

    def deleteProfile(self, button):
        profile_name = self.list_profile.getSelectedValue()
        if profile_name:
            self.host.bridge.deleteProfile(profile_name)
            self.__refillProfiles()
        self.host.removePopUp()
        
    def onNewProfile(self, e):
        pop_up_widget = InputDialog(_("New profile"), _("Please enter a new profile name"), cancel_cb=self.cancelDialog, ok_cb=self.newProfile)
        self.host.showPopUp(pop_up_widget)

    def onDeleteProfile(self, e):
        pop_up_widget = ConfirmDialog(_("Are you sure you want to delete the profile %s ?") % self.list_profile.getSelectedValue(), no_cb=self.cancelDialog, yes_cb=self.deleteProfile)
        self.host.showPopUp(pop_up_widget)

    def onProfileChange(self, list_wid):
        def setJID(jabberID):
            self.login_wid.set_edit_text(jabberID)
            self.host.redraw()
        def setPassword(password):
            self.pass_wid.set_edit_text(password)
            self.host.redraw()

        profile_name = list_wid.getSelectedValue()
        if profile_name:
            self.host.bridge.asyncGetParamA("JabberID", "Connection", profile_key=profile_name, callback=setJID, errback=self.getParamError)
            self.host.bridge.asyncGetParamA("Password", "Connection", profile_key=profile_name, callback=setPassword, errback=self.getParamError)
        
    def onConnectProfile(self, button):
        profile_name = self.list_profile.getSelectedValue()
        if not profile_name:
            pop_up_widget = Alert(_('No profile selected'), _('You need to create and select a profile before connecting'), ok_cb=self.cancelDialog)
            self.host.showPopUp(pop_up_widget)
        elif profile_name[0] == '@':
            pop_up_widget = Alert(_('Bad profile name'), _("A profile name can't start with a @"), ok_cb=self.cancelDialog)
            self.host.showPopUp(pop_up_widget)
        else:
            profile = self.host.bridge.getProfileName(profile_name)
            assert(profile)
            #TODO: move this to quick_app
            self.host.bridge.asyncGetParamA("JabberID", "Connection", profile_key=profile,
                                            callback=lambda old_jid: self.__old_jidReceived(old_jid, profile), errback=self.getParamError)

    def __old_jidReceived(self, old_jid, profile):
        self.host.bridge.asyncGetParamA("Password", "Connection", profile_key=profile,
                                        callback=lambda old_pass: self.__old_passReceived(old_jid, old_pass, profile), errback=self.getParamError)
    
    def __old_passReceived(self, old_jid, old_pass, profile):
        """Check if we have new jid/pass, save them if it is the case, and plug profile"""
        new_jid = self.login_wid.get_edit_text()
        new_pass = self.pass_wid.get_edit_text()

        if old_jid != new_jid:
            self.host.bridge.setParam("JabberID", new_jid, "Connection", profile)
            self.host.bridge.setParam("Server", JID(new_jid).domain, "Connection", profile)
        if old_pass != new_pass:
            self.host.bridge.setParam("Password", new_pass, "Connection", profile)
        self.host.plug_profile(profile)
            
    def getParamError(self, ignore):
        popup = Alert("Error", _("Can't get profile parameter"), ok_cb=self.host.removePopUp)
        self.host.showPopUp(popup)
