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
from logging import debug, info, error
from sat.tools.jid  import JID


class Profile(wx.Frame):
    """This class is used to show/modify profile given by SàT"""

    def __init__(self, host, data, title="Profile"):
        super(Profile, self).__init__(None, title=title)
        self.host = host

        self.name_dict = { 'fullname': _('Full Name'),
                           'nick' : _('Nickname'),
                           'birthday' : _('Birthday'),
                           'phone' : _('Phone #'),
                           'website' : _('Website'),
                           'email' : _('E-mail'),
                           'avatar' : _('Avatar')
                         }
        self.ctl_list = {}  # usefull to access ctrl, key = (name)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.notebook=wx.Notebook(self, -1)
        self.sizer.Add(self.notebook, 1, flag=wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        
        #events
        self.Bind(wx.EVT_CLOSE, self.onClose, self)
        
        self.MakeModal()
        self.showData(data)
        self.Show()

    def showData(self, data):
        flags = wx.TE_READONLY
        
        #General tab
        generaltab = wx.Panel(self.notebook)
        sizer = wx.FlexGridSizer(cols=2)
        sizer.AddGrowableCol(1)
        generaltab.SetSizer(sizer)
        generaltab.SetAutoLayout(True)
        for field in ['fullname','nick', 'birthday', 'phone', 'website', 'email']:        
            value = data[field] if data.has_key(field) else ''
            label=wx.StaticText(generaltab, -1, self.name_dict[field]+": ")
            sizer.Add(label)
            self.ctl_list[field] = wx.TextCtrl(generaltab, -1, value, style = flags)
            sizer.Add(self.ctl_list[field], 1, flag = wx.EXPAND)
        #Avatar
        if data.has_key('avatar'):
            filename = self.host.bridge.getAvatarFile(data['avatar'])
            label=wx.StaticText(generaltab, -1, self.name_dict['avatar']+": ")
            sizer.Add(label)
            img = wx.Image(filename).ConvertToBitmap()
            self.ctl_list['avatar'] = wx.StaticBitmap(generaltab, -1, img)
            sizer.Add(self.ctl_list['avatar'], 0)


        
        self.notebook.AddPage(generaltab, _("General"))


    def onClose(self, event):
        """Close event"""
        debug(_("close"))
        self.MakeModal(False)
        event.Skip()

