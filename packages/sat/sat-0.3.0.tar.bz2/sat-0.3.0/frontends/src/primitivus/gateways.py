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
from urwid_satext import sat_widgets
from sat_frontends.quick_frontend.quick_gateways import QuickGatewaysManager
from sat.tools.jid import JID


class GatewaysManager(urwid.WidgetWrap, QuickGatewaysManager):

    def __init__(self, host, gateways, title=_("Gateways manager"), server=None):
        QuickGatewaysManager.__init__(self, host, gateways, server)
        if server:
            title+=" (%s)" % server
        widget_list = urwid.SimpleListWalker([])
        widget_list.append(urwid.Text(self.WARNING_MSG))
        widget_list.append(urwid.Divider('-'))
        for gateway in gateways:
            self.addGateway(widget_list,gateway, gateways[gateway])
        widget_list.append(urwid.Divider())
        self.ext_serv = sat_widgets.AdvancedEdit(_("Use external XMPP server: "))
        go_button = sat_widgets.CustomButton( _("GO !"),self.browseExternalServer)
        ext_serv_col = urwid.Columns([self.ext_serv,('fixed',go_button.getSize(),go_button)])
        widget_list.append(ext_serv_col)
        list_wid = urwid.ListBox(widget_list)
        decorated = sat_widgets.LabelLine(list_wid, sat_widgets.SurroundedText(title))
        urwid.WidgetWrap.__init__(self, decorated)
    
    def browseExternalServer(self, button):
        """Open the gateway manager on given server"""
        server = self.ext_serv.get_edit_text()
        if not server:
            popup = sat_widgets.Alert(_("Error"), _("You must enter an external server JID"), ok_cb=self.host.removePopUp)
            self.host.showPopUp(popup)
            return
        action_id = self.host.bridge.findGateways(server, self.host.profile)
        self.host.current_action_ids.add(action_id)
        self.host.current_action_ids_cb[action_id] = self.host.onGatewaysFound
        self.host.removeWindow()

    def addGateway(self, widget_list, gateway, param):
       
        widget_col = []
        widget_col.append(('weight',4,urwid.Text(unicode(param['name'])))) #FIXME: unicode to be remove when DBus bridge will not give dbus.String anymore
       
        #Then the transport type message
        widget_col.append(('weight',6,urwid.Text(self.getGatewayDesc(param['type']))))

        #The buttons
        
        reg_button = sat_widgets.CustomButton( _("Register"), self.onRegister)
        reg_button.gateway_jid = JID(gateway)
        widget_col.append(('fixed',reg_button.getSize(),reg_button))
        unreg_button = sat_widgets.CustomButton( _("Unregister"), self.onUnregister)
        unreg_button.gateway_jid = JID(gateway)
        widget_col.append(('fixed',unreg_button.getSize(),unreg_button))
        widget_list.append(urwid.Columns(widget_col,1))
        
    def onRegister(self, button):
        """Called when register button is clicked"""
        gateway_jid = button.gateway_jid
        action_id = self.host.bridge.in_band_register(gateway_jid, self.host.profile)
        self.host.current_action_ids.add(action_id)

    def onUnregister(self, button):
        """Called when unregister button is clicked"""
        gateway_jid = button.gateway_jid
        action_id = self.host.bridge.gatewayRegister("CANCEL",gateway_jid, None, self.host.profile)
        self.host.current_action_ids.add(action_id)
