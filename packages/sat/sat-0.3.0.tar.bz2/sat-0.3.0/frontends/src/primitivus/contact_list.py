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
from sat_frontends.quick_frontend.quick_contact_list import QuickContactList
from sat_frontends.quick_frontend.quick_utils import escapePrivate, unescapePrivate
from sat.tools.jid import JID


class ContactList(urwid.WidgetWrap, QuickContactList):
    signals = ['click','change']

    def __init__(self, host, on_click=None, on_change=None, user_data=None):
        QuickContactList.__init__(self)
        self.host = host
        self.selected = None
        self.groups={}
        self.alert_jid=set()
        self.show_status = False
        self.show_disconnected = False
        
        #we now build the widget
        self.frame = urwid.Frame(self.__buildList())
        self.main_widget = sat_widgets.LabelLine(self.frame, sat_widgets.SurroundedText(_("Contacts")))
        urwid.WidgetWrap.__init__(self, self.main_widget)
        if on_click:
            urwid.connect_signal(self, 'click', on_click, user_data)
        if on_change:
            urwid.connect_signal(self, 'change', on_change, user_data)

    def update(self):
        """Update display, keep focus"""
        widget, position = self.frame.body.get_focus()
        self.frame.body = self.__buildList()
        if position:
            self.frame.body.set_focus(position)
        self.host.redraw()

    def update_jid(self, jid):
        self.update()

    def keypress(self, size, key):
        if key == "meta s": #user wants to (un)hide contacts' statuses
            self.show_status = not self.show_status
            self.update()
        elif key == "meta d": #user wants to (un)hide disconnected contacts
            self.show_disconnected = not self.show_disconnected
            self.update()
        return super(ContactList, self).keypress(size, key) 
    
    def __contains__(self, jid):
        for group in self.groups:
            if jid.short in self.groups[group][1]:
                return True
        return False

    def setFocus(self, name, select=False):
        """give focus to the first group or contact wich contain the given name
        @param name: name to check
        @param select: if True, the contact/group is also clicked"""
        idx = 0
        for widget in self.frame.body.body:
            try:
                if name in widget.getValue():
                    self.frame.body.set_focus(idx)
                    if select:
                        self.__contactClicked(widget, True)
                    return
            except AttributeError:
                pass
            idx+=1

    def putAlert(self, jid):
        """Put an alert on the jid to get attention from user (e.g. for new message)"""
        self.alert_jid.add(jid.short)
        self.update()

    def __groupClicked(self, group_wid):
        group = self.groups[group_wid.getValue()]
        group[0] = not group[0]
        self.update()
        self.setFocus(group_wid.getValue())

    def __contactClicked(self, contact_wid, selected):
        self.selected = contact_wid.data
        for widget in self.frame.body.body:
            if widget.__class__ == sat_widgets.SelectableText:
                widget.setState(widget.data == self.selected, invisible=True)
        if self.selected in self.alert_jid:
            self.alert_jid.remove(self.selected)
        self.host.modeHint('INSERTION')
        self.update()
        self._emit('click')

    def __buildContact(self, content, param_contacts):
        """Add contact representation in widget list
        @param content: widget list, e.g. SimpleListWalker
        @param contacts: list of JID"""
        contacts = list(param_contacts)
        
        widgets = [] #list of built widgets
        
        for contact in contacts:
            if contact.startswith(const_PRIVATE_PREFIX):
                contact_disp = ('alert' if contact in self.alert_jid else "show_normal", unescapePrivate(contact))
                show_icon = ''
                status = ''
            else:
                jid=JID(contact)
                name = self.getCache(jid, 'name')
                nick = self.getCache(jid, 'nick')
                status = self.getCache(jid, 'status')
                show = self.getCache(jid, 'show')
                if show == None:
                    show = "unavailable"
                if (not self.show_disconnected and show == "unavailable"
                    and not contact in self.alert_jid and contact != self.selected):
                    continue
                show_icon, show_attr = const_SHOW_ICON.get(show,('','default'))
                contact_disp = ('alert' if contact in self.alert_jid else show_attr, nick or name or jid.node or jid.short)
            display = [ show_icon + " " , contact_disp]
            if self.show_status:
                status_disp = ('status',"\n  " + status) if status else ""
                display.append(status_disp)
            header = '(*) ' if contact in self.alert_jid else ''
            widget = sat_widgets.SelectableText(display,
                                                selected = contact==self.selected,
                                                header=header)
            widget.data = contact
            widget.comp = contact_disp[1].lower() #value to use for sorting
            widgets.append(widget)
       
        widgets.sort(key=lambda widget: widget.comp)

        for widget in widgets:
            content.append(widget)
            urwid.connect_signal(widget, 'change', self.__contactClicked)

    def __buildSpecials(self, content):
        """Build the special entities"""
        specials = self.specials.keys()
        specials.sort()
        for special in specials:
            jid=JID(special) 
            name = self.getCache(jid, 'name')
            nick = self.getCache(jid, 'nick')
            special_disp = ('alert' if special in self.alert_jid else 'default', nick or name or jid.node or jid.short)
            display = [ "  " , special_disp]
            header = '(*) ' if special in self.alert_jid else ''
            widget = sat_widgets.SelectableText(display,
                                                selected = special==self.selected,
                                                header=header)
            widget.data = special
            content.append(widget)
            urwid.connect_signal(widget, 'change', self.__contactClicked)

    def __buildList(self):
        """Build the main contact list widget"""
        content = urwid.SimpleListWalker([])
        
        self.__buildSpecials(content)
        if self.specials:
            content.append(urwid.Divider('='))

        group_keys = self.groups.keys()
        group_keys.sort(key = lambda x: x.lower() if x else x)
        for key in group_keys:
            unfolded = self.groups[key][0]
            if key!=None:
                header = '[-]' if unfolded else '[+]'
                widget = sat_widgets.ClickableText(key,header=header+' ')
                content.append(widget)
                urwid.connect_signal(widget, 'click', self.__groupClicked)
            if unfolded:
                self.__buildContact(content, self.groups[key][1])
        return urwid.ListBox(content)

    def unselectAll(self):
        """Unselect all contacts"""
        self.selected = None
        for widget in self.frame.body.body:
            if widget.__class__ == sat_widgets.SelectableText:
                widget.setState(False, invisible=True)


    def getContact(self):
        """Return contact currently selected"""
        return self.selected
            
    def clearContacts(self):
        """clear all the contact list"""
        QuickContactList.clearContacts(self)
        self.groups={}
        self.selected = None
        self.unselectAll()
        self.update()

    def replace(self, jid, groups=None, attributes=None):
        """add a contact to the list if doesn't exist, else update it"""
        QuickContactList.replace(self, jid, groups, attributes)
        if jid.short in self.specials:
            return
        if not groups:
            groups = [None]
        if not attributes:
            attributes={}
        assert isinstance(groups, list)
        assert isinstance(jid, JID)
        for group in groups:
            if not self.groups.has_key(group):
                self.groups[group] = [True,set()]  #[unfold,list_of_contacts]
            self.groups[group][1].add(jid.short)
        self.update()


        """contacts = self.list_wid.getAllValues()
        if jid.short not in contacts:
            contacts.append(jid.short)
            contacts.sort()
            self.list_wid.changeValues(contacts)
            self._emit('change')"""
    
    def remove(self, jid):
        """remove a contact from the list"""
        QuickContactList.remove(self, jid)
        groups_to_remove = []
        for group in self.groups:
            contacts = self.groups[group][1]
            if jid.short in contacts:
                contacts.remove(jid.short)
                if not len(contacts):
                    groups_to_remove.append(group)
        for group in groups_to_remove:
            del self.groups[group]
        self.update()
    
    def add(self, jid, param_groups=[None]):
        """add a contact to the list"""
        self.replace(jid,param_groups)

    def setSpecial(self, special_jid, special_type):
        """Set entity as a special
        @param jid: jid of the entity
        @param _type: special type (e.g.: "MUC")
        """
        QuickContactList.setSpecial(self, special_jid, special_type)
        if None in self.groups:
            folded,group_jids = self.groups[None]
            for group_jid in group_jids:
                if JID(group_jid).short == special_jid.short:
                    group_jids.remove(group_jid)
                    break
        self.update()

    def updatePresence(self, jid, show, priority, statuses):
        #XXX: for the moment, we ignore presence updates for special entities
        if jid.short not in self.specials:
            QuickContactList.updatePresence(self, jid, show, priority, statuses)
