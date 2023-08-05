#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SAT: a jabber client
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

from logging import debug, info, error
from xml.dom import minidom
from wokkel import data_form
import pdb
from twisted.words.xish import domish

"""This library help manage XML used in SàT (parameters, registration, etc) """

    
def dataForm2xml(form):
    """Take a data form (xep-0004, Wokkel's implementation) and convert it to a SàT xml"""
    
    form_ui = XMLUI("form", "vertical")

    if form.instructions:
        form_ui.addText('\n'.join(form.instructions), 'instructions')
    
    labels = filter(lambda field:field.label,form.fieldList)
    if labels:
        #if there is no label, we don't need to use pairs
        form_ui.changeLayout("pairs")
    
    for field in form.fieldList:
        if field.fieldType == 'fixed':
            __field_type = 'text'
        elif field.fieldType == 'text-single':
            __field_type = "string"
        elif field.fieldType == 'text-private':
            __field_type = "password"
        elif field.fieldType == 'list-single':
            __field_type = "list"
        else:
            error (u"FIXME FIXME FIXME: Type [%s] is not managed yet by SàT" % field.fieldType)
            __field_type = "string"
        
        if labels:
            if field.label:
                form_ui.addLabel(field.label)
            else:
                form_ui.addEmpty()

        elem = form_ui.addElement(__field_type, field.var, field.value, [option.value for option in field.options]) 
    return form_ui.toXml()

def tupleList2dataForm(values):
    """convert a list of tuples (name,value) to a wokkel submit data form"""
    form = data_form.Form('submit')
    for value in values:
        field = data_form.Field(var=value[0], value=value[1])
        form.addField(field)

    return form

def paramsXml2xmlUI(xml):
    """Convert the xml for parameter to a SàT XML User Interface"""
    params_doc = minidom.parseString(xml.encode('utf-8'))
    top = params_doc.documentElement
    if top.nodeName != 'params':
        error(_('INTERNAL ERROR: parameters xml not valid'))
        assert(False)
    param_ui = XMLUI("param", "tabs")
    for category in top.getElementsByTagName("category"):
        name = category.getAttribute('name')
        label = category.getAttribute('label')
        if not name:
            error(_('INTERNAL ERROR: params categories must have a name'))
            assert(False)
        param_ui.addCategory(name, 'pairs', label=label)
        for param in category.getElementsByTagName("param"):
            name = param.getAttribute('name')
            label = param.getAttribute('label')
            if not name:
                error(_('INTERNAL ERROR: params must have a name'))
                assert(False)
            type = param.getAttribute('type')
            value = param.getAttribute('value') or None
            callback_id = param.getAttribute('callback_id') or None
            if type == "button":
                param_ui.addEmpty()
            else:
                param_ui.addLabel(label or name)
            param_ui.addElement(name=name, type=type, value=value, callback_id=callback_id)

    return param_ui.toXml()

    


class XMLUI:
    """This class is used to create a user interface (form/window/parameters/etc) using SàT XML"""

    def __init__(self, panel_type, layout="vertical", title=None):
        """Init SàT XML Panel
        @param panel_type: one of
            - window (new window)
            - form (formulaire, depend of the frontend, usually a panel with cancel/submit buttons)
            - param (parameters, presentatio depend of the frontend)
        @param layout: disposition of elements, one of:
            - vertical: elements are disposed up to bottom
            - horizontal: elements are disposed left to right
            - pairs: elements come on two aligned columns
              (usually one for a label, the next for the element)
            - tabs: elemens are in categories with tabs (notebook)
        @param title: title or default if None
        """
        if not panel_type in ['window', 'form', 'param']:
            error(_("Unknown panel type [%s]") % panel_type)
            assert(False)
        self.type = panel_type
        impl = minidom.getDOMImplementation()

        self.doc = impl.createDocument(None, "sat_xmlui", None)
        top_element = self.doc.documentElement
        top_element.setAttribute("type", panel_type)
        if title:
            top_element.setAttribute("title", title)
        self.parentTabsLayout = None #used only we have 'tabs' layout
        self.currentCategory = None #used only we have 'tabs' layout
        self.changeLayout(layout)

    def __del__(self):
        self.doc.unlink() 
    
    def __createLayout(self, layout, parent=None):
        """Create a layout element
        @param type: layout type (cf init doc)
        @parent: parent element or None
        """
        if not layout in ['vertical', 'horizontal', 'pairs', 'tabs']:
            error (_("Unknown layout type [%s]") % layout)
            assert (False)
        layout_elt = self.doc.createElement('layout')
        layout_elt.setAttribute('type',layout)
        if parent != None:
            parent.appendChild(layout_elt)
        return layout_elt

    def __createElem(self, type, name=None, parent = None):
        """Create an element
        @param type: one of
            - empty: empty element (usefull to skip something in a layout, e.g. skip first element in a PAIRS layout)
            - text: text to be displayed in an multi-line area, e.g. instructions
        @param name: name of the element or None
        @param parent: parent element or None
        """
        elem = self.doc.createElement('elem')
        if name:
            elem.setAttribute('name', name)
        elem.setAttribute('type', type)
        if parent != None:
            parent.appendChild(elem)
        return elem

    def changeLayout(self, layout):
        """Change the current layout"""
        self.currentLayout = self.__createLayout(layout, self.currentCategory if self.currentCategory else self.doc.documentElement)
        if layout == "tabs":
            self.parentTabsLayout = self.currentLayout


    def addEmpty(self, name=None):
        """Add a multi-lines text"""
        elem = self.__createElem('empty', name, self.currentLayout)
    
    def addText(self, text, name=None):
        """Add a multi-lines text"""
        elem = self.__createElem('text', name, self.currentLayout)
        text = self.doc.createTextNode(text)
        elem.appendChild(text)

    def addLabel(self, text, name=None):
        """Add a single line text, mainly useful as label before element"""
        elem = self.__createElem('label', name, self.currentLayout)
        elem.setAttribute('value', text)

    def addString(self, name=None, value=None):
        """Add a string box"""
        elem = self.__createElem('string', name, self.currentLayout)
        if value:
            elem.setAttribute('value', value)
    
    def addPassword(self, name=None, value=None):
        """Add a password box"""
        elem = self.__createElem('password', name, self.currentLayout)
        if value:
            elem.setAttribute('value', value)

    def addTextBox(self, name=None, value=None):
        """Add a string box"""
        elem = self.__createElem('textbox', name, self.currentLayout)
        if value:
            elem.setAttribute('value', value)
    
    def addBool(self, name=None, value="true"):
        """Add a string box"""
        assert value in ["true","false"]
        elem = self.__createElem('bool', name, self.currentLayout)
        elem.setAttribute('value', value)
    
    def addList(self, options, name=None, value=None, style=set()):
        """Add a list of choices"""
        styles = set(style)
        assert (options)
        assert (styles.issubset(['multi'])) 
        elem = self.__createElem('list', name, self.currentLayout)
        self.addOptions(options, elem) 
        if value:
            elem.setAttribute('value', value)
        for style in styles:
            elem.setAttribute(style, 'yes')

    def addButton(self, callback_id, name, value, fields_back=[]):
        """Add a button
        @param callback: callback which will be called if button is pressed
        @param name: name
        @param value: label of the button
        @fields_back: list of names of field to give back when pushing the button"""
        elem = self.__createElem('button', name, self.currentLayout)
        elem.setAttribute('callback_id', callback_id)
        elem.setAttribute('value', value)
        for field in fields_back:
            fback_el = self.doc.createElement('field_back')
            fback_el.setAttribute('name', field)
            elem.appendChild(fback_el)


    
    def addElement(self, type, name = None, value = None, options = None, callback_id = None):
        """Convenience method to add element, the params correspond to the ones in addSomething methods"""
        if type == 'empty':
            self.addEmpty(name)
        elif type == 'text':
            assert(value!=None)
            self.addText(value, name)
        elif type == 'label':
            assert(value)
            self.addLabel(value)
        elif type == 'string':
            self.addString(name, value)
        elif type == 'password':
            self.addPassword(name, value)
        elif type == 'textbox':
            self.addTextBox(name, value)
        elif type == 'bool':
            if not value:
                value = "true"
            self.addBool(name, value)
        elif type == 'list':
            self.addList(options, name, value)
        elif type == 'button':
            assert(callback_id and value)
            self.addButton(callback_id, name, value)

    def addOptions(self, options, parent):
        """Add options to a multi-values element (e.g. list)
        @param parent: multi-values element"""
        for option in options:
            opt = self.doc.createElement('option')
            opt.setAttribute('value', option)
            parent.appendChild(opt)

    def addCategory(self, name, layout, label=None):
        """Add a category to current layout (must be a tabs layout)"""
        assert(layout != 'tabs')
        if not self.parentTabsLayout:
            error(_("Trying to add a category without parent tabs layout"))
            assert(False)
        if self.parentTabsLayout.getAttribute('type') != 'tabs':
            error(_("parent layout of a category is not tabs"))
            assert(False)

        if not label:
            label = name
        self.currentCategory = cat = self.doc.createElement('category')
        cat.setAttribute('name', name)
        cat.setAttribute('label', label)
        self.changeLayout(layout)
        self.parentTabsLayout.appendChild(cat)

    def toXml(self):
        """return the XML representation of the panel""" 
        return self.doc.toxml()



class ElementParser(object):
    """callable class to parse XML string into Element
    Found at http://stackoverflow.com/questions/2093400/how-to-create-twisted-words-xish-domish-element-entirely-from-raw-xml/2095942#2095942
    (c) Karl Anderson"""

    def __call__(self, s):
        self.result = None
        def onStart(el):
            self.result = el
        def onEnd():
            pass
        def onElement(el):
            self.result.addChild(el)

        parser = domish.elementStream()
        parser.DocumentStartEvent = onStart
        parser.ElementEvent = onElement
        parser.DocumentEndEvent = onEnd
        tmp = domish.Element((None, "s"))
        tmp.addRawXml(s.replace('\n','').replace('\t',''))
        parser.parse(tmp.toXml().encode('utf-8'))
        return self.result.firstChildElement() 
