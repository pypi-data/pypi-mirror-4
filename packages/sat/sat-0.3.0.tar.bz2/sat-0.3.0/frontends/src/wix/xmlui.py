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
from logging import debug, info, warning, error
from sat.tools.jid  import JID


class XMLUI(wx.Frame):
    """Create an user interface from a SàT xml"""

    def __init__(self, host, xml_data='', title="Form", options = None, misc = None):
        style = wx.DEFAULT_FRAME_STYLE & ~wx.CLOSE_BOX if 'NO_CANCEL' in options else wx.DEFAULT_FRAME_STYLE #FIXME: gof: Q&D tmp hack
        super(XMLUI, self).__init__(None, title=title, style=style)

        self.host = host
        self.options = options or []
        self.misc = misc or {}
        self.ctrl_list = {}  # usefull to access ctrl

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        
        #events
        if not 'NO_CANCEL' in self.options:
            self.Bind(wx.EVT_CLOSE, self.onClose, self)
        
        self.MakeModal()

        self.constructUI(xml_data)

        self.Show()

    def __parseElems(self, node, parent):
        """Parse elements inside a <layout> tags, and add them to the parent sizer"""
        for elem in node.childNodes:
            if elem.nodeName != "elem":
                message=_("Unmanaged tag")
                error(message)
                raise Exception(message)
            _proportion = 0
            id = elem.getAttribute("id")
            name = elem.getAttribute("name")
            type = elem.getAttribute("type")
            value = elem.getAttribute("value") if elem.hasAttribute('value') else u''
            if type=="empty":
                ctrl = wx.Window(parent, -1)
            elif type=="text":
                try:
                    value = elem.childNodes[0].wholeText
                except IndexError:
                    warning (_("text node has no child !"))
                ctrl = wx.StaticText(parent, -1, value)
            elif type=="label":
                ctrl = wx.StaticText(parent, -1, value+": ")
            elif type=="string":
                ctrl = wx.TextCtrl(parent, -1, value)
                self.ctrl_list[name] = ({'type':type, 'control':ctrl})
                _proportion = 1
            elif type=="password":
                ctrl = wx.TextCtrl(parent, -1, value, style=wx.TE_PASSWORD)
                self.ctrl_list[name] = ({'type':type, 'control':ctrl})
                _proportion = 1 
            elif type=="textbox":
                ctrl = wx.TextCtrl(parent, -1, value, style=wx.TE_MULTILINE)
                self.ctrl_list[name] = ({'type':type, 'control':ctrl})
                _proportion = 1
            elif type=="bool":
                ctrl = wx.CheckBox(panel, -1, "", style = wx.CHK_2STATE)
                ctrl.SetValue(value=="true")
                self.ctrl_list[name] = ({'type':type, 'control':ctrl})
                _proportion = 1
            elif type=="list":
                style=wx.LB_MULTIPLE if elem.getAttribute("multi")=='yes' else wx.LB_SINGLE
                ctrl = wx.ListBox(parent, -1, choices=[option.getAttribute("value") for option in elem.getElementsByTagName("option")], style=style)
                self.ctrl_list[name] = ({'type':type, 'control':ctrl})
                _proportion = 1
            elif type=="button":
                callback_id = elem.getAttribute("callback_id")
                ctrl = wx.Button(parent, -1, value)
                ctrl.param_id = (callback_id,[field.getAttribute('name') for field in elem.getElementsByTagName("field_back")])
                parent.Bind(wx.EVT_BUTTON, self.onButtonClicked, ctrl)
            else:
                error(_("FIXME FIXME FIXME: type [%s] is not implemented") % type)  #FIXME !
                raise NotImplementedError
            parent.sizer.Add(ctrl, _proportion, flag=wx.EXPAND)

    def __parseChilds(self, parent, current_param, elem, wanted = ['layout']):
        """Recursively parse childNodes of an elemen
        @param parent: parent wx.Window
        @param current_param: current wx.Window (often wx.Panel) or None if we must create one
        @param elem: element from which childs will be parsed
        @param wanted: list of tag names that can be present in the childs to be SàT XMLUI compliant"""
        for node in elem.childNodes:
            if wanted and not node.nodeName in wanted:
                raise Exception("Invalid XMLUI") #TODO: make a custom exception
            if node.nodeName == "layout":
                _proportion = 0
                type = node.getAttribute('type')
                if type == "tabs":
                    current = wx.Notebook(parent, -1, style=wx.NB_LEFT if self.type=='param' else 0)
                    self.__parseChilds(current, None, node, ['category'])
                    _proportion = 1
                else:
                    if current_param == None:
                        current = wx.Panel(parent, -1)
                    else:
                        current = current_param
                    if type == "vertical":
                        current.sizer = wx.BoxSizer(wx.VERTICAL)
                    elif type == "pairs":
                        current.sizer = wx.FlexGridSizer(cols=2)
                        current.sizer.AddGrowableCol(1) #The growable column need most of time to be the right one in pairs
                    else:
                        warning(_("Unknown layout, using default one"))
                        current.sizer = wx.BoxSizer(wx.VERTICAL)
                    current.SetSizer(current.sizer)
                    self.__parseElems(node, current)
                if parent:
                    parent.sizer.Add(current, _proportion, flag=wx.EXPAND)
            elif node.nodeName == "category":
                name = node.getAttribute('name') 
                label = node.getAttribute('label') 
                if not node.nodeName in wanted or not name or not isinstance(parent,wx.Notebook):
                    raise Exception("Invalid XMLUI") #TODO: make a custom exception
                notebook = parent
                tab_panel = wx.Panel(notebook, -1) 
                tab_panel.sizer = wx.BoxSizer(wx.VERTICAL)
                tab_panel.SetSizer(tab_panel.sizer)
                notebook.AddPage(tab_panel, label or name)
                self.__parseChilds(tab_panel, None, node, ['layout'])

            else:
                message=_("Unknown tag")
                error(message)
                raise Exception(message) #TODO: raise a custom exception here


    def constructUI(self, xml_data):
        panel=wx.Panel(self)
        panel.sizer = wx.BoxSizer(wx.VERTICAL)
        
        cat_dom = minidom.parseString(xml_data.encode('utf-8'))
        top= cat_dom.documentElement
        self.type = top.getAttribute("type")
        self.title = top .getAttribute("title")
        if self.title:
            self.SetTitle(self.title)
        if top.nodeName != "sat_xmlui" or not self.type in ['form', 'param', 'window']:
            raise Exception("Invalid XMLUI") #TODO: make a custom exception

        self.__parseChilds(panel, None, cat_dom.documentElement)

        if self.type == 'form':
            dialogButtons = wx.StdDialogButtonSizer()
            submitButton = wx.Button(panel,wx.ID_OK, label=_("Submit"))
            dialogButtons.AddButton(submitButton)
            panel.Bind(wx.EVT_BUTTON, self.onFormSubmitted, submitButton)
            if not 'NO_CANCEL' in self.options:
                cancelButton = wx.Button(panel,wx.ID_CANCEL)
                dialogButtons.AddButton(cancelButton)
                panel.Bind(wx.EVT_BUTTON, self.onFormCancelled, cancelButton)
            dialogButtons.Realize()
            panel.sizer.Add(dialogButtons, flag=wx.ALIGN_CENTER_HORIZONTAL)

        panel.SetSizer(panel.sizer)
        panel.SetAutoLayout(True)
        panel.sizer.Fit(self)
        self.sizer.Add(panel, 1, flag=wx.EXPAND)
        cat_dom.unlink()

    ###events

    def onButtonClicked(self, event):
        """Called when a button is pushed"""
        callback_id, fields = event.GetEventObject().param_id
        data = {"callback_id":callback_id}
        for field in fields:
            ctrl = self.ctrl_list[field]
            if isinstance(ctrl['control'], wx.ListBox):
                data[field] = '\t'.join([ctrl['control'].GetString(idx) for idx in ctrl['control'].GetSelections()])
            else:
                data[field] = ctrl['control'].GetValue()

        id = self.host.bridge.launchAction("button", data, profile_key = self.host.profile)
        self.host.current_action_ids.add(id)
        event.Skip()

    def onFormSubmitted(self, event):
        """Called when submit button is clicked"""
        debug(_("Submitting form"))
        data = []
        for ctrl_name in self.ctrl_list:
            ctrl = self.ctrl_list[ctrl_name]
            if isinstance(ctrl['control'], wx.ListBox):
                data.append((ctrl_name, ctrl['control'].GetStringSelection()))
            elif isinstance(ctrl['control'], wx.CheckBox):
                data.append((ctrl_name, "true" if ctrl['control'].GetValue() else "false"))
            else:
                data.append((ctrl_name, ctrl['control'].GetValue()))
        if self.misc.has_key('action_back'): #FIXME FIXME FIXME: WTF ! Must be cleaned
            id = self.misc['action_back']("SUBMIT",self.misc['target'], data)
            self.host.current_action_ids.add(id)
        elif self.misc.has_key('callback'):
            self.misc['callback'](data)
        else:
            warning (_("The form data is not sent back, the type is not managed properly"))
        self.MakeModal(False)
        self.Destroy()
        
    def onFormCancelled(self, event):
        """Called when cancel button is clicked"""
        debug(_("Cancelling form"))
        self.MakeModal(False)
        self.Close()
   
    def onClose(self, event):
        """Close event: we have to send the form."""
        debug(_("close"))
        self.MakeModal(False)
        event.Skip()

