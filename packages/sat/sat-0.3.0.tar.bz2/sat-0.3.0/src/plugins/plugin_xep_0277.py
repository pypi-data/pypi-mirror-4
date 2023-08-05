#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SAT plugin for microblogging over XMPP (xep-0277)
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
from twisted.internet import protocol
from twisted.words.protocols.jabber import client, jid
from twisted.words.protocols.jabber import error as jab_error
import twisted.internet.error
from twisted.words.xish import domish
from sat.tools.xml_tools import ElementParser

from wokkel import disco,pubsub
from feed.atom import Entry, Author
import uuid
from time import time

NS_MICROBLOG = 'urn:xmpp:microblog:0'
OPT_ACCESS_MODEL = 'pubsub#access_model'
OPT_PERSIST_ITEMS = 'pubsub#persist_items'
OPT_MAX_ITEMS = 'pubsub#max_items'
OPT_DELIVER_PAYLOADS = 'pubsub#deliver_payloads'
OPT_SEND_ITEM_SUBSCRIBE = 'pubsub#send_item_subscribe'

PLUGIN_INFO = {
"name": "Microblogging over XMPP Plugin",
"import_name": "XEP-0277",
"type": "XEP",
"protocols": [],
"dependencies": ["XEP-0163","XEP-0060"],
"main": "XEP_0277",
"handler": "no",
"description": _("""Implementation of microblogging Protocol""")
}

class NodeAccessChangeException(Exception):
    pass

class XEP_0277():

    def __init__(self, host):
        info(_("Microblogging plugin initialization"))
        self.host = host
        self.host.plugins["XEP-0163"].addPEPEvent("MICROBLOG", NS_MICROBLOG, self.microblogCB, self.sendMicroblog)
        host.bridge.addMethod("getLastMicroblogs", ".plugin",
                              in_sign='sis', out_sign='aa{ss}',
                              method=self.getLastMicroblogs,
                              async = True,
                              doc = { 'summary':'retrieve items',
                                      'param_0':'jid: publisher of wanted microblog',
                                      'param_1':'max_items: see XEP-0060 #6.5.7',
                                      'param_2':'%(doc_profile)s',
                                      'return':'list of microblog data (dict)'
                                    })
        host.bridge.addMethod("setMicroblogAccess", ".plugin", in_sign='ss', out_sign='',
                               method=self.setMicroblogAccess,
                               async = True,
                               doc = {
                                     })

    def item2mbdata(self, item):
        """Convert an XML Item to microblog data used in bridge API
        @param item: domish.Element of microblog item
        @return: microblog data (dictionary)"""
        try:
            entry_elt = filter (lambda x:x.name == "entry", item.children)[0]
        except KeyError:
            warning(_('No entry element in microblog item'))
            return
        _entry = Entry().import_xml(entry_elt.toXml().encode('utf-8'))
        microblog_data={}
        try:
            microblog_data['content'] = _entry.title.text
            if len(_entry.authors):
                microblog_data['author'] = _entry.authors[0].name.text
            microblog_data['timestamp'] = str(int(_entry.updated.tf))
            microblog_data['id'] = item['id']
        except (AttributeError, KeyError):
            error(_('Error while parsing atom entry for microblogging event'))
            return {}

        ##XXX: workaround for Jappix behaviour
        if not 'author' in microblog_data:
            from xe import NestElement
            try:
                author=NestElement('author')
                author.import_xml(str(_entry))
                microblog_data['author'] = author.nick.text
            except:
                error(_('Cannot find author'))
        ##end workaround Jappix
        return microblog_data

    def microblogCB(self, itemsEvent, profile):
        for item in itemsEvent.items:
            microblog_data = self.item2mbdata(item)
            self.host.bridge.personalEvent(itemsEvent.sender.full(), "MICROBLOG", microblog_data, profile)

    def data2entry(self, data, profile):
        """Convert a data dict to en entry usable to create an item
        @param data: data dict as given by bridge method
        @return: domish.Element"""
        _uuid = unicode(uuid.uuid1())
        content = data['content']
        _entry = Entry()
        #FIXME: need to escape html
        _entry.title = unicode(content).encode('utf-8')
        _entry.author = Author()
        _entry.author.name = data.get('author',self.host.getJidNStream(profile)[0].userhost()).encode('utf-8')
        _entry.updated = float(data.get('timestamp',time()))
        _entry.id = str(_uuid)
        _entry_elt = ElementParser()(str(_entry).decode('utf-8'))
        item = pubsub.Item(payload=_entry_elt)
        item['id'] = _uuid
        return item

    def sendMicroblog(self, data, profile):
        """Send XEP-0277's microblog data
        @param data: must include content
        @param profile: profile which send the mood"""
        if not data.has_key('content'):
            error(_("Microblog data must contain at least 'content' key"))
            return 3
        content = data['content']
        if not content:
            error(_("Microblog data's content value must not be empty"))
            return 3
        item = self.data2entry(data, profile)
        self.host.plugins["XEP-0060"].publish(None, NS_MICROBLOG, [item], profile_key = profile)
        return 0

    def getLastMicroblogs(self, pub_jid, max_items=10, profile_key='@DEFAULT@'):
        """Get the last published microblogs
        @param pub_jid: jid of the publisher
        @param max_items: how many microblogs we want to get
        @param profile_key: profile key
        @param callback: used for the async answer
        @param errback: used for the async answer
        """
        assert(callback)
        d = self.host.plugins["XEP-0060"].getItems(jid.JID(pub_jid), NS_MICROBLOG, max_items=max_items, profile_key=profile_key)
        d.addCallback(lambda items: map(self.item2mbdata, items))
        
    def setMicroblogAccess(self, access="presence", profile_key='@DEFAULT@'):
        """Create a microblog node on PEP with given access
        If the node already exists, it change options
        @param access: Node access model, according to xep-0060 #4.5
        @param profile_key: profile key"""

        _jid, xmlstream = self.host.getJidNStream(profile_key)
        if not _jid:
            error(_("Can't find profile's jid"))
            return
        _options = {OPT_ACCESS_MODEL:access, OPT_PERSIST_ITEMS:1, OPT_MAX_ITEMS:-1, OPT_DELIVER_PAYLOADS:1, OPT_SEND_ITEM_SUBSCRIBE: 1}
        
        def cb(result):
            #Node is created with right permission
            debug(_("Microblog node has now access %s") % access)

        def fatal_err(s_error):
            #Something went wrong
            error(_("Can't set microblog access"))
            raise NodeAccessChangeException()

        def err_cb(s_error):
            #If the node already exists, the condition is "conflict",
            #else we have an unmanaged error
            if s_error.value.condition=='conflict':
                #d = self.host.plugins["XEP-0060"].deleteNode(_jid.userhostJID(), NS_MICROBLOG, profile_key=profile_key)
                #d.addCallback(lambda x: create_node().addCallback(cb).addErrback(fatal_err))
                change_node_options().addCallback(cb).addErrback(fatal_err)
            else:
                fatal_err(s_error)
        
        def create_node():
            return self.host.plugins["XEP-0060"].createNode(_jid.userhostJID(), NS_MICROBLOG, _options, profile_key=profile_key)
        
        def change_node_options():
            return self.host.plugins["XEP-0060"].setOptions(_jid.userhostJID(), NS_MICROBLOG, _jid.userhostJID(), _options, profile_key=profile_key)

        create_node().addCallback(cb).addErrback(err_cb)

        
        
