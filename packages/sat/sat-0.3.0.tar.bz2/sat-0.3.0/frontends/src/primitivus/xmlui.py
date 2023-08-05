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
from logging import debug, info, warning, error
from xml.dom import minidom

class Pairs(urwid.WidgetWrap):

    def __init__(self, weight_0='1', weight_1='1'):
        self.idx = 0
        self.weight_0 = weight_0
        self.weight_1 = weight_1
        columns = urwid.Columns([urwid.Text(''), urwid.Text('')])
        #XXX: empty Text hack needed because Pile doesn't support empty list
        urwid.WidgetWrap.__init__(self,columns)

    def append(self, widget):
        pile = self._w.widget_list[self.idx]
        if isinstance(pile, urwid.Text):
            self._w.widget_list[self.idx] = urwid.Pile([widget])
            if self.idx == 1:
                self._w.set_focus(1)
        else:
            pile.widget_list.append(widget)
            pile.item_types.append(('weight',getattr(self,'weight_'+str(self.idx))))
        self.idx = (self.idx + 1) % 2
        
class InvalidXMLUI(Exception):
    pass

class XMLUI(urwid.WidgetWrap):
    
    def __init__(self, host, xml_data, title = None, options = None, misc = None):
        self.host = host
        self.title = title
        self.options = options or []
        self.misc = misc or {}
        self.__dest = "window"
        self.ctrl_list = {}  # usefull to access ctrl
        widget = self.constructUI(xml_data)
        urwid.WidgetWrap.__init__(self,widget)

    def __parseElems(self, node, parent):
        """Parse elements inside a <layout> tags, and add them to the parent"""
        for elem in node.childNodes:
            if elem.nodeName != "elem":
                message=_("Unmanaged tag")
                error(message)
                raise Exception(message)
            id = elem.getAttribute("id")
            name = elem.getAttribute("name")
            type = elem.getAttribute("type")
            value = elem.getAttribute("value") if elem.hasAttribute('value') else u''
            if type=="empty":
                ctrl = urwid.Text('') 
            elif type=="text":
                try:
                    value = elem.childNodes[0].wholeText
                except IndexError:
                    warning (_("text node has no child !"))
                ctrl = urwid.Text(value)
            elif type=="label":
                ctrl = urwid.Text(value+": ")
            elif type=="string":
                ctrl = sat_widgets.AdvancedEdit(edit_text = value)
                self.ctrl_list[name] = ({'type':type, 'control':ctrl})
            elif type=="password":
                ctrl = sat_widgets.Password(edit_text = value)
                self.ctrl_list[name] = ({'type':type, 'control':ctrl})
            elif type=="textbox":
                ctrl = sat_widgets.AdvancedEdit(edit_text = value, multiline=True)
                self.ctrl_list[name] = ({'type':type, 'control':ctrl})
            elif type=="bool":
                ctrl = urwid.CheckBox('', state = value=="true")
                self.ctrl_list[name] = ({'type':type, 'control':ctrl})
            elif type=="list":
                style=[] if elem.getAttribute("multi")=='yes' else ['single']
                ctrl = sat_widgets.List(options=[option.getAttribute("value") for option in elem.getElementsByTagName("option")], style=style)
                self.ctrl_list[name] = ({'type':type, 'control':ctrl})
            elif type=="button":
                callback_id = elem.getAttribute("callback_id")
                ctrl = sat_widgets.CustomButton(value, on_press=self.onButtonPress)
                ctrl.param_id = (callback_id,[field.getAttribute('name') for field in elem.getElementsByTagName("field_back")])
            else:
                error(_("FIXME FIXME FIXME: type [%s] is not implemented") % type)  #FIXME !
                raise NotImplementedError
            if self.type == 'param':
                if isinstance(ctrl,urwid.Edit) or isinstance(ctrl,urwid.CheckBox):
                    urwid.connect_signal(ctrl,'change',self.onParamChange)
                ctrl._param_category = self._current_category
                ctrl._param_name = name
            parent.append(ctrl)

    def __parseChilds(self, current, elem, wanted = ['layout'], data = None):
        """Recursively parse childNodes of an elemen
        @param current: widget container with 'append' method
        @param elem: element from which childs will be parsed
        @param wanted: list of tag names that can be present in the childs to be SàT XMLUI compliant"""
        for node in elem.childNodes:
            if wanted and not node.nodeName in wanted:
                raise InvalidXMLUI
            if node.nodeName == "layout":
                type = node.getAttribute('type')
                if type == "tabs":
                    tab_cont = sat_widgets.TabsContainer()
                    self.__parseChilds(current, node, ['category'], tab_cont)
                    current.append(tab_cont)
                elif type == "vertical":
                    self.__parseElems(node, current)
                elif type == "pairs":
                    pairs = Pairs()
                    self.__parseElems(node, pairs)
                    current.append(pairs)
                else:
                    warning(_("Unknown layout, using default one"))
                    self.__parseElems(node, current)
            elif node.nodeName == "category":
                name = node.getAttribute('name') 
                label = node.getAttribute('label') 
                if not name or not isinstance(data,sat_widgets.TabsContainer):
                    raise InvalidXMLUI 
                if self.type == 'param':
                    self._current_category = name #XXX: awful hack because params need category and we don't keep parent
                tab_cont = data
                listbox = tab_cont.addTab(label or name)
                self.__parseChilds(listbox.body, node, ['layout'])
            else:
                message=_("Unknown tag")
                error(message)
                raise NotImplementedError

    def constructUI(self, xml_data):
        
        ret_wid = urwid.ListBox(urwid.SimpleListWalker([]))
        
        cat_dom = minidom.parseString(xml_data.encode('utf-8'))
        top=cat_dom.documentElement
        self.type = top.getAttribute("type")
        self.title = top.getAttribute("title") or self.title
        if top.nodeName != "sat_xmlui" or not self.type in ['form', 'param', 'window']:
            raise InvalidXMLUI

        if self.type == 'param':
            self.param_changed = set()

        self.__parseChilds(ret_wid.body, cat_dom.documentElement)

        assert ret_wid.body
        
        if isinstance(ret_wid.body[0],sat_widgets.TabsContainer):
            ret_wid = ret_wid.body[0] #xxx: awfull hack cause TabsContainer is a BoxWidget, can't be inside a ListBox
        
        
        if self.type == 'form':
            buttons = []
            buttons.append(urwid.Button(_('Submit'),self.onFormSubmitted))
            if not 'NO_CANCEL' in self.options:
                buttons.append(urwid.Button(_('Cancel'),self.onFormCancelled))
            max_len = max([len(button.get_label()) for button in buttons])
            grid_wid = urwid.GridFlow(buttons,max_len+4,1,0,'center')
            ret_wid.body.append(grid_wid)
        elif self.type == 'param':
            assert(isinstance(ret_wid,sat_widgets.TabsContainer))
            buttons = []
            buttons.append(sat_widgets.CustomButton(_('Save'),self.onSaveParams))
            buttons.append(sat_widgets.CustomButton(_('Cancel'),lambda x:self.host.removeWindow()))
            max_len = max([button.getSize() for button in buttons])
            grid_wid = urwid.GridFlow(buttons,max_len,1,0,'center')
            ret_wid.addFooter(grid_wid)
        return ret_wid

    def show(self,show_type = 'popup'):
        """Show the constructed UI
        @param show_type: how to show the UI:
            - popup
            - window"""
        self.__dest = "popup"
        decorated = sat_widgets.LabelLine(self, sat_widgets.SurroundedText(self.title or '')) 
        if show_type == 'popup':
            self.host.showPopUp(decorated)
        elif show_type == 'window':
            self.host.addWindow(decorated)
        else:
            error(_('INTERNAL ERROR: Unmanaged show_type (%s)') % show_type)
            assert(False)
        self.host.redraw()


    ##EVENTS##

    def onButtonPress(self, button):
        callback_id, fields = button.param_id
        data = {"callback_id":callback_id}
        for field in fields:
            ctrl = self.ctrl_list[field]
            if isinstance(ctrl['control'],sat_widgets.List):
                data[field] = '\t'.join(ctrl['control'].getSelectedValues())
            else:
                data[field] = ctrl['control'].getValue()

        id = self.host.bridge.launchAction("button", data, profile_key = self.host.profile)
        self.host.current_action_ids.add(id)

    def onParamChange(self, widget, extra=None):
        """Called when type is param and a widget to save is modified"""
        assert(self.type == "param")
        self.param_changed.add(widget)

    def onFormSubmitted(self, button):
        data = []
        for ctrl_name in self.ctrl_list:
            ctrl = self.ctrl_list[ctrl_name]
            if isinstance(ctrl['control'], sat_widgets.List):
                data.append((ctrl_name, ctrl['control'].getSelectedValue()))
            elif isinstance(ctrl['control'], urwid.CheckBox):
                data.append((ctrl_name, "true" if ctrl['control'].get_state() else "false"))
            else:
                data.append((ctrl_name, ctrl['control'].get_edit_text()))
        if self.misc.has_key('action_back'): #FIXME FIXME FIXME: WTF ! Must be cleaned
            raise NotImplementedError
            self.host.debug()
        elif self.misc.has_key('callback'):
            self.misc['callback'](data)
        else:
            warning (_("The form data is not sent back, the type is not managed properly"))
        self.host.removePopUp()
    
    def onFormCancelled(self, button):
        if self.__dest == 'window':
            self.host.removeWindow()
        else:
            self.host.removePopUp()

    def onSaveParams(self, button):
        for ctrl in self.param_changed:
            if isinstance(ctrl, urwid.CheckBox):
                value = "true" if ctrl.get_state() else "false"
            else:
                value = ctrl.get_edit_text()
            self.host.bridge.setParam(ctrl._param_name, value, ctrl._param_category, profile_key = self.host.profile)
        self.host.removeWindow()
