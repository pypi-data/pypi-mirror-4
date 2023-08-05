#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SàT plugin for managing raw XML log 
Copyright (C) 2011  Jérôme Poisson (goffi@goffi.org)

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
from twisted.words.protocols.jabber.xmlstream import XmlStream
from twisted.words.xish import domish

PLUGIN_INFO = {
"name": "Raw XML log Plugin",
"import_name": "XmlLog",
"type": "Misc",
"protocols": [],
"dependencies": [],
"main": "XmlLog",
"handler": "no",
"description": _("""Send raw XML logs to bridge""")
}

class LoggingXmlStream(XmlStream):
    """This class send the raw XML to the Bridge, for logging purpose"""

    def send(self, obj):
        if isinstance(obj,basestring):
            log=unicode(obj)
        elif isinstance(obj, domish.Element):
            log=obj.toXml()
        else:
            error(_('INTERNAL ERROR: Unmanaged XML type'))
        self._host.bridge.xmlLog("OUT", log, self._profile)
        return XmlStream.send(self, obj)

    def dataReceived(self, data):
        self._host.bridge.xmlLog("IN", data.decode('utf-8'), self._profile)
        return XmlStream.dataReceived(self, data)
    

class XmlLog():
    
    params = """
    <params>
    <general>
    <category name="Debug">
        <param name="Xml log" label="%(label_xmllog)s" value="false" type="bool" />
    </category>
    </general>
    </params>
    """ % {"label_xmllog": _("Activate XML log")}

    def __init__(self, host):
        info(_("Plugin XML Log initialization"))
        self.host = host
        
        #parameters
        host.memory.importParams(self.params)
        
        #bridge
        host.bridge.addSignal("xmlLog", ".plugin", signature='sss') #args: direction("IN" or "OUT"), xml_data, profile
        
        do_log = self.host.memory.getParamA("Xml log", "Debug")
        if do_log:
            info(_("XML log activated"))
            host.trigger.add("XML Initialized", self.logXml)
       
    def logXml(self, xmlstream, profile):
        xmlstream.__class__ = LoggingXmlStream
        xmlstream._profile = profile
        xmlstream._host = self.host
        return True
