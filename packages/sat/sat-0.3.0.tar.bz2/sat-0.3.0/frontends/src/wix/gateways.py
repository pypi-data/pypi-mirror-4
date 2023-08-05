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
from sat_frontends.quick_frontend.quick_gateways import QuickGatewaysManager

class GatewaysManager(wx.Frame,QuickGatewaysManager):

    def __init__(self, host, gateways, title=_("Gateways manager"), server=None):
        wx.Frame.__init__(self, None, title=title)
        QuickGatewaysManager.__init__(self, host, gateways, server)

        if server:
            self.SetTitle(title+" (%s)" % server)
            
        #Fonts
        self.normal_font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.bold_font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.italic_font = wx.Font(8, wx.DEFAULT, wx.FONTSTYLE_ITALIC, wx.NORMAL)
        self.button_font = wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.BOLD)


        self.modified = {}  # dict of modified data (i.e. what we have to save)
        self.ctl_list = {}  # usefull to access ctrl, key = (name, category)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        warning = wx.TextCtrl(self, -1, value=self.WARNING_MSG, style = wx.TE_MULTILINE |
                                                                       wx.TE_READONLY |
                                                                       wx.TE_LEFT)
        warning.SetFont(self.bold_font)
        self.sizer.Add(warning, 0, wx.EXPAND)
        warning.ShowPosition(0)
        self.panel = wx.Panel(self)
        self.panel.sizer = wx.FlexGridSizer(cols=5)
        self.panel.SetSizer(self.panel.sizer)
        self.panel.SetAutoLayout(True)
        self.sizer.Add(self.panel, 1, flag=wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        
        #events
        self.Bind(wx.EVT_CLOSE, self.onClose, self)
        
        self.MakeModal()
        self.panel.sizer.Add(wx.Window(self.panel, -1))
        title_name = wx.StaticText(self.panel, -1, "Name")
        title_name.SetFont(self.bold_font)
        title_type = wx.StaticText(self.panel, -1, "Type")
        title_type.SetFont(self.bold_font)
        self.panel.sizer.Add(title_name)
        self.panel.sizer.Add(title_type)
        self.panel.sizer.Add(wx.Window(self.panel, -1))
        self.panel.sizer.Add(wx.Window(self.panel, -1))
    
        for gateway in gateways:
            self.addGateway(gateway, gateways[gateway])

        self.ext_server_panel = wx.Panel(self)
        self.ext_server_panel.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ext_server_panel.SetSizer(self.ext_server_panel.sizer)
        self.ext_server_panel.SetAutoLayout(True)
        self.sizer.Add(self.ext_server_panel, 0, flag=wx.EXPAND)

        ext_server_label = wx.StaticText(self.ext_server_panel, -1, _("Use external XMPP server: "))
        ext_server_label.SetFont(wx.ITALIC_FONT)
        self.ext_server_text = wx.TextCtrl(self.ext_server_panel, -1)
        ext_server_button =  wx.Button(self.ext_server_panel, -1, _("GO !"))
        self.ext_server_panel.Bind(wx.EVT_BUTTON, self.browseExternalServer, ext_server_button)

        self.ext_server_panel.sizer.Add(ext_server_label)
        self.ext_server_panel.sizer.Add(self.ext_server_text, 1, flag=wx.EXPAND)
        self.ext_server_panel.sizer.Add(ext_server_button)
        
        #self.panel.sizer.Fit(self)
        self.sizer.Fit(self)
        
        self.Show()

    def browseExternalServer(self, event):
        """Open the gateway manager on given server"""
        server = self.ext_server_text.GetValue()
        debug(_("Opening gateways manager on [%s]") % server) 
        id = self.host.bridge.findGateways(server, self.host.profile)
        self.host.current_action_ids.add(id)
        self.host.current_action_ids_cb[id] = self.host.onGatewaysFound
        self.MakeModal(False) 
        self.Destroy()


    def addGateway(self, gateway, param):

        #First The icon
        isz = (16,16)
        im_icon = wx.StaticBitmap(self.panel, -1, wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR, isz))

        #Then the name

        label=wx.StaticText(self.panel, -1, param['name'])
        label.SetFont(self.normal_font)
       
        #Then the transport type message
        type_label_txt = self.getGatewayDesc(param['type'])

        type_label = wx.StaticText(self.panel, -1, type_label_txt)
        type_label.SetFont(self.italic_font)

        #The buttons
        def register_cb(event):
            """Called when register button is clicked"""
            gateway_jid = event.GetEventObject().gateway_jid
            id = self.host.bridge.in_band_register(gateway_jid, self.host.profile)
            self.host.current_action_ids.add(id)
            self.MakeModal(False) 
            self.Destroy()

        def unregister_cb(event):
            """Called when unregister button is clicked"""
            gateway_jid = event.GetEventObject().gateway_jid
            id = self.host.bridge.gatewayRegister("CANCEL",gateway_jid, None, self.host.profile)
            self.host.current_action_ids.add(id)
            self.MakeModal(False) 
            self.Destroy()
        
        reg_button = wx.Button(self.panel, -1, _("Register"), size=wx.Size(-1, 8))
        reg_button.SetFont(self.button_font)
        reg_button.gateway_jid = JID(gateway)
        self.panel.Bind(wx.EVT_BUTTON, register_cb, reg_button)
        unreg_button = wx.Button(self.panel, -1, _("Unregister"), size=wx.Size(-1, 8))
        unreg_button.SetFont(self.button_font)
        unreg_button.gateway_jid = JID(gateway)
        self.panel.Bind(wx.EVT_BUTTON, unregister_cb, unreg_button)
        
        self.panel.sizer.Add(im_icon)
        self.panel.sizer.Add(label)
        self.panel.sizer.Add(type_label)
        self.panel.sizer.Add(reg_button, 1, wx.EXPAND)
        self.panel.sizer.Add(unreg_button, 1, wx.EXPAND)


    def onClose(self, event):
        """Close event"""
        debug(_("close"))
        self.MakeModal(False)
        event.Skip()

