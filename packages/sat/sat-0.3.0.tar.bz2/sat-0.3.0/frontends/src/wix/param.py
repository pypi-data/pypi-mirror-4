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
import pdb
from xml.dom import minidom
from logging import debug, info, error
from sat.tools.jid  import JID


class Param(wx.Frame):
    def __init__(self, host, title=_("Configuration")):
        super(Param, self).__init__(None, title=title)

        self.host = host

        self.modified = {}  # dict of modified data (i.e. what we have to save)
        self.ctl_list = {}  # usefull to access ctrl, key = (name, category)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.notebook=wx.Notebook(self, -1, style=wx.NB_LEFT)
        self.sizer.Add(self.notebook, 1, flag=wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        
        #events
        self.Bind(wx.EVT_CLOSE, self.onClose, self)
        
        self.MakeModal()

        for category in self.host.bridge.getParamsCategories():
            self.addCategory(category)
        
        self.Show()

    def addCategory(self, category):
        panel=wx.Panel(self.notebook)
        panel.sizer = wx.BoxSizer(wx.VERTICAL)

        def errorGettingParams(ignore):
            wx.MessageDialog(self, _("Can't get parameters"), _("Parameters error"), wx.ICON_ERROR).ShowModal()

        def gotParams(result):
            cat_dom = minidom.parseString(result.encode('utf-8'))
            
            for param in cat_dom.documentElement.getElementsByTagName("param"):
                name = param.getAttribute("name")
                label = param.getAttribute("label")
                type = param.getAttribute("type")
                value = param.getAttribute("value")
                sizer = wx.BoxSizer(wx.HORIZONTAL)
                if type=="string":
                    label=wx.StaticText(panel, -1, (label or name)+" ")
                    ctrl = wx.TextCtrl(panel, -1, value)
                    sizer.Add(label)
                elif type=="password":
                    label=wx.StaticText(panel, -1, (label or name)+" ")
                    ctrl = wx.TextCtrl(panel, -1, value, style=wx.TE_PASSWORD)
                    sizer.Add(label)
                elif type=="bool":
                    ctrl = wx.CheckBox(panel, -1, label or name, style = wx.CHK_2STATE)
                    ctrl.SetValue(value=="true")
                elif type=="button":
                    ctrl = wx.Button(panel, -1, value)
                    ctrl.callback_id = param.getAttribute("callback_id")
                else:
                    error(_("FIXME FIXME FIXME"))  #FIXME !
                    raise NotImplementedError
                if name:
                    ctrl.param_id=(name, category)
                    self.ctl_list[(name, category)] = ctrl
                sizer.Add(ctrl, 1, flag=wx.EXPAND)
                panel.sizer.Add(sizer, flag=wx.EXPAND)

                if type=="string" or type=="password":
                    panel.Bind(wx.EVT_TEXT, self.onTextChanged, ctrl)
                elif type=="bool":
                    panel.Bind(wx.EVT_CHECKBOX, self.onCheckBoxClicked, ctrl)
                elif type=="button":
                    panel.Bind(wx.EVT_BUTTON, self.onButtonClicked, ctrl)

            panel.SetSizer(panel.sizer)
            panel.SetAutoLayout(True)
            self.notebook.AddPage(panel, category)
            cat_dom.unlink()

        self.host.bridge.getParamsForCategory(category, profile_key = self.host.profile, callback = gotParams, errback = errorGettingParams)

    def onTextChanged(self, event):
        """Called when a string paramater is modified"""
        self.modified[event.GetEventObject().param_id]=event.GetString()
        
        ### FIXME # Some hacks for better presentation, should be generic # FIXME ###
        if event.GetEventObject().param_id == ('JabberID', 'Connection'):
            domain = JID(event.GetString()).domain
            self.ctl_list[('Server', 'Connection')].SetValue(domain)
            self.modified[('Server', 'Connection')] = domain 

        event.Skip()
        
    def onCheckBoxClicked(self, event):
        """Called when a bool paramater is modified"""
        self.modified[event.GetEventObject().param_id]="true" if event.GetEventObject().GetValue() else "false"
        event.Skip()
        
    def onButtonClicked(self, event):
        """Called when a button paramater is modified"""
        self.__save_parameters()
        name, category = event.GetEventObject().param_id
        callback_id = event.GetEventObject().callback_id
        data = {"name":name, "category":category, "callback_id":callback_id}
        id = self.host.bridge.launchAction("button", data, profile_key = self.host.profile)
        self.host.current_action_ids.add(id)
        event.Skip()

    def __save_parameters(self):
        for param in self.modified:
            self.host.bridge.setParam(param[0], self.modified[param], param[1], profile_key = self.host.profile)
        self.modified.clear()

    def onClose(self, event):
        """Close event: we have to save the params."""
        debug(_("close"))
        #now we save the modifier params
        self.__save_parameters()

        self.MakeModal(False)
        event.Skip()

