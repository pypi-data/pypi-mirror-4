#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SAT plugin for managing xep-0077
Copyright (C) 2009, 2010, 2011, 2012, 2013 Jérôme Poisson (goffi@goffi.org)

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
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber.xmlstream import IQ
from sat.tools.xml_tools import dataForm2xml

from wokkel import data_form

NS_REG = 'jabber:iq:register'

PLUGIN_INFO = {
"name": "XEP 0077 Plugin",
"import_name": "XEP-0077",
"type": "XEP",
"protocols": ["XEP-0077"],
"dependencies": [],
"main": "XEP_0077",
"description": _("""Implementation of in-band registration""")
}

class XEP_0077():
 
    def __init__(self, host):
        info(_("Plugin XEP_0077 initialization"))
        self.host = host
        self.triggers = {}  #used by other protocol (e.g. XEP-0100) to finish registration. key = target_jid
        host.bridge.addMethod("in_band_register", ".plugin", in_sign='ss', out_sign='s', method=self.in_band_register)
        host.bridge.addMethod("in_band_submit", ".plugin", in_sign='ssa(ss)s', out_sign='s', method=self.in_band_submit)
   
    def addTrigger(self, target, cb, profile):
        """Add a callback which is called when registration to target is successful"""
        self.triggers[target] = (cb, profile)
    
    def reg_ok(self, answer, profile):
        """Called after the first get IQ"""
        try:
            x_elem = filter (lambda x:x.name == "x", answer.firstChildElement().elements())[0] #We only want the "x" element (data form)
        except IndexError:
            info(_("No data form found"))
            #TODO: manage registration without data form
            answer_data={"reason": "unmanaged", "message":_("This gateway can't be managed by SàT, sorry :(")}
            answer_type = "ERROR"
            self.host.bridge.actionResult(answer_type, answer['id'], answer_data, profile)
            return
        
        form = data_form.Form.fromElement(x_elem)
        xml_data = dataForm2xml(form)
        self.host.bridge.actionResult("XMLUI", answer['id'], {"target":answer["from"], "type":"registration", "xml":xml_data}, profile)

    def reg_err(self, failure, profile):
        """Called when something is wrong with registration"""
        info (_("Registration failure: %s") % str(failure.value))
        answer_data = {}
        answer_data['reason'] = 'unknown'
        answer_data={"message":"%s [code: %s]" % (failure.value.condition, unicode(failure.value))}
        answer_type = "ERROR"
        self.host.bridge.actionResult(answer_type, failure.value.stanza['id'], answer_data, profile)
   
    def unregistrationAnswer(self, answer, profile):
        debug (_("registration answer: %s") % answer.toXml())
        answer_type = "SUCCESS"
        answer_data={"message":_("Your are now unregistred")}
        self.host.bridge.actionResult(answer_type, answer['id'], answer_data, profile)
        
    def unregistrationFailure(self, failure, profile):
        info (_("Unregistration failure: %s") % str(failure.value))
        answer_type = "ERROR"
        answer_data = {}
        answer_data['reason'] = 'unknown'
        answer_data={"message":_("Unregistration failed: %s") % failure.value.condition}
        self.host.bridge.actionResult(answer_type, failure.value.stanza['id'], answer_data, profile)
    
    def registrationAnswer(self, answer, profile):
        debug (_("registration answer: %s") % answer.toXml())
        answer_type = "SUCCESS"
        answer_data={"message":_("Registration successfull")}
        self.host.bridge.actionResult(answer_type, answer['id'], answer_data, profile)
        if self.triggers.has_key(answer["from"]):
            callback,profile = self.triggers[answer["from"]]
            callback(answer["from"], profile)
            del self.triggers[answer["from"]]
        
    def registrationFailure(self, failure, profile):
        info (_("Registration failure: %s") % str(failure.value))
        print failure.value.stanza.toXml()
        answer_type = "ERROR"
        answer_data = {}
        if failure.value.condition == 'conflict':
            answer_data['reason'] = 'conflict'
            answer_data={"message":_("Username already exists, please choose an other one")}
        else:
            answer_data['reason'] = 'unknown'
            answer_data={"message":_("Registration failed")}
        self.host.bridge.actionResult(answer_type, failure.value.stanza['id'], answer_data, profile)
        if failure.value.stanza["from"] in self.triggers.has_key:
            del self.triggers[failure.value.stanza["from"]]

    def in_band_submit(self, action, target, fields, profile):
        """Submit a form for registration, using data_form"""
        id, deferred = self.host.submitForm(action, target, fields, profile)
        if action == 'CANCEL':
            deferred.addCallbacks(self.unregistrationAnswer, self.unregistrationFailure, callbackArgs=[profile], errbackArgs=[profile])
        else:    
            deferred.addCallbacks(self.registrationAnswer, self.registrationFailure, callbackArgs=[profile], errbackArgs=[profile])
        return id
    
    def in_band_register(self, target, profile_key='@DEFAULT@'):
        """register to a target JID"""
        client = self.host.getClient(profile_key)
        if not client:
            error (_('Asking for an non-existant or not connected profile'))
            return ""
        to_jid = jid.JID(target)
        debug(_("Asking registration for [%s]") % to_jid.full())
        reg_request=IQ(client.xmlstream,'get')
        reg_request["from"]=client.jid.full()
        reg_request["to"] = to_jid.full()
        reg_request.addElement('query', NS_REG)
        reg_request.send(to_jid.full()).addCallbacks(self.reg_ok, self.reg_err, callbackArgs=[client.profile], errbackArgs=[client.profile])
        return reg_request["id"] 
