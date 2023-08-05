#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SAT plugin for managing xep-0045
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

from logging import debug, info, warning, error
from twisted.words.xish import domish
from twisted.internet import protocol, defer, threads, reactor
from twisted.words.protocols.jabber import client, jid, xmlstream
from twisted.words.protocols.jabber import error as jab_error
from twisted.words.protocols.jabber.xmlstream import IQ
from twisted.web.client import getPage
from sat.memory.persistent import PersistentBinaryDict
import os.path
import pdb

from zope.interface import implements

from wokkel import disco, iwokkel, data_form
from sat.tools.xml_tools import XMLUI
import urllib
import webbrowser

from BeautifulSoup import BeautifulSoup
import re


PLUGIN_INFO = {
"name": "CouchSurfing plugin",
"import_name": "CS",
"type": "Misc",
"protocols": [],
"dependencies": [],
"main": "CS_Plugin",
"handler": "no",
"description": _(u"""This plugin allow to manage your CouchSurfing account throught your SàT frontend""")
}

AGENT = 'Salut à Toi XMPP/CS Plugin'

class CS_Plugin():

    params = """
    <params>
    <individual>
    <category name="CouchSurfing">
        <param name="Login" type="string" />
        <param name="Password" type="password" />
    </category>
    </individual>
    </params>
    """

    def __init__(self, host):
        info(_("Plugin CS initialization"))
        self.host = host
        #parameters
        host.memory.importParams(CS_Plugin.params)
        #menu
        host.importMenu(_("Plugin"), "CouchSurfing", self.menuSelected, help_string = _("Launch CoushSurfing management interface"))
        self.data={} #TODO: delete cookies/data after a while
        self.host.registerGeneralCB("plugin_CS_sendMessage", self.sendMessage)
        self.host.registerGeneralCB("plugin_CS_showUnreadMessages", self.showUnreadMessages)

    def profileConnected(self, profile):
        self.data[profile] = PersistentBinaryDict("plugin_CS", profile)
        def dataLoaded(ignore):
            if not self.data[profile]:
                self.data[profile] = {'cookies':{}}
                
        self.data[profile].load().addCallback(dataLoaded)

    def profileDisconnected(self, profile):
        del self.data[profile]

    def erroCB(self, e, id):
        """Called when something is going wrong when contacting CS website"""
        #pdb.set_trace()
        message_data={"reason": "connection error", "message":_(u"Impossible to contact CS website, please check your login/password, connection or try again later")}
        self.host.bridge.actionResult("ERROR", id, message_data)

    def menuSelected(self, id, profile):
        """Called when the couchsurfing menu item is selected"""
        login = self.host.memory.getParamA("Login", "CouchSurfing", profile_key=profile)
        password = self.host.memory.getParamA("Password", "CouchSurfing", profile_key=profile)
        if not login or not password:
            message_data={"reason": "uncomplete", "message":_(u"You have to fill your CouchSurfing login & password in parameters before using this interface")}
            self.host.bridge.actionResult("ERROR", id, message_data)
            return

        post_data = urllib.urlencode({'auth_login[un]':login,'auth_login[pw]':password,'auth_login[action]':'Login...'}) 
        
        self.data[profile]['cookies'] = {}
        
        d = getPage('http://www.couchsurfing.org/login.html', method='POST', postdata=post_data, headers={'Content-Type':'application/x-www-form-urlencoded'} , agent=AGENT, cookies=self.data[profile]['cookies'])
        d.addCallback(self.__connectionCB, id, profile)
        d.addErrback(self.erroCB, id)

        #self.host.bridge.actionResult("SUPPRESS", id, {})


#pages parsing callbacks
    def savePage(self, name, html):
        f = open ('/tmp/CS_'+name+'.html','w')
        f.write(html)
        f.close()
        print "page [%s] sauvee" % name
        #pdb.set_trace()

    def __connectionCB(self, html, id, profile):
        print 'Response received'
        #self.savePage('principale',html)
        soup = BeautifulSoup(html)
        self.data[profile]['user_nick'] = soup.find('a','item_link',href='/home.html').contents[0]
        self.data[profile]['user_name'] = soup.html.head.title.string.split(' - ')[1]
        #unread messages
        try:
            self.data[profile]['unread_messages'] = int(soup.find(lambda tag: tag.name=='div' and ('class','item_bubble') in tag.attrs and tag.find('a', href="/messages.html?message_status=inbox")).find(text=True))
        except:
            self.data[profile]['unread_messages'] = 0
        #unread couchrequest messages
        try:
            self.data[profile]['unread_CR_messages'] = int(soup.find(lambda tag: tag.name=='div' and ('class','item_bubble') in tag.attrs and tag.find('a', href="/couchmanager")).find(text=True))
        except:
            self.data[profile]['unread_CR_messages'] = 0

        #if we have already the list of friend, no need to make new requests
        if not self.data[profile].has_key('friends'):
            self.data[profile]['friends'] = {}
            d = getPage('http://www.couchsurfing.org/connections.html?type=myfriends&show=10000', agent=AGENT, cookies=self.data[profile]['cookies'])
            d.addCallback(self.__friendsPageCB, id=id, profile=profile)
            d.addErrback(self.erroCB, id)
        else:
            self.host.bridge.actionResult("XMLUI", id, {"type":"window", "xml":self.__buildUI(self.data[profile])})

    def __buildUI(self, data):
        """Build the XML UI of the plugin
        @param data: data store for the profile"""
        user_nick = data['user_nick']
        user_name = data['user_name']
        unread_mess = data['unread_messages']
        unread_CR_mess = data['unread_CR_messages']
        friends_list = data['friends'].keys()
        friends_list.sort()
        interface = XMLUI('window','tabs', title='CouchSurfing management')
        interface.addCategory(_("Messages"), "vertical")
        interface.addText(_("G'day %(name)s, you have %(nb_message)i unread message%(plural_mess)s and %(unread_CR_mess)s unread couch request message%(plural_CR)s\nIf you want to send a message, select the recipient(s) in the list below") % {'name':user_name, 'nb_message':unread_mess, 'plural_mess':'s' if unread_mess>1 else '', 'unread_CR_mess': unread_CR_mess, 'plural_CR':'s' if unread_CR_mess>1 else ''})
        if unread_mess:
            interface.addButton('plugin_CS_showUnreadMessages', 'showUnreadMessages', _('Show unread message%(plural)s in external web browser') % {'plural':'s' if unread_mess>1 else ''})
        interface.addList(friends_list, 'friends', style=['multi'])
        interface.changeLayout('pairs')
        interface.addLabel(_("Subject"))
        interface.addString('subject')
        interface.changeLayout('vertical')
        interface.addLabel(_("Message"))
        interface.addText("(use %name% for contact name and %firstname% for guessed first name)")
        interface.addTextBox('message')
        interface.addButton('plugin_CS_sendMessage', 'sendMessage', _('send'), fields_back=['friends','subject','message'])
        #interface.addCategory(_("Events"), "vertical") #TODO: coming soon, hopefuly :)
        #interface.addCategory(_("Couch search"), "vertical")
        return interface.toXml()

    def __meetingPageCB(self, html):
        """Called when the meeting page has been received"""

    def __friendsPageCB(self, html, id, profile):
        """Called when the friends list page has been received"""
        self.savePage('friends',html)
        soup = BeautifulSoup(html.replace('"formtable width="400','"formtable" width="400"')) #CS html fix #TODO: report the bug to CS dev team
        friends = self.data[profile]['friends']
        for _tr in soup.findAll('tr', {'class':re.compile("^msgRow*")}): #we parse the row with friends infos
            _nobr = _tr.find('nobr')  #contain the friend name
            friend_name = unicode(_nobr.string)
            friend_link = u'http://www.couchsurfing.org'+_nobr.parent['href']
            regex_href = re.compile(r'/connections\.html\?id=([^&]+)')
            a_tag = _tr.find('a',href=regex_href)
            friend_id = regex_href.search(unicode(a_tag)).groups()[0]

            debug(_("CS friend found: %(friend_name)s (id: %(friend_id)s, link: %(friend_link)s)") % {'friend_name':friend_name, 'friend_id':friend_id, 'friend_link':friend_link})
            friends[friend_name] = {'link':friend_link,'id':friend_id} 
        a = soup.find('td','barmiddle next').a  #is there several pages ?
        if a:
            #yes, we parse the next page
            d = getPage('http://www.couchsurfing.org/'+str(a['href']), agent=AGENT, cookies=self.data[profile]['cookies'])
            d.addCallback(self.__friendsPageCB, id=id, profile=profile)
            d.addErrback(self.erroCB, id)
        else:
            #no, we show the result
            self.host.bridge.actionResult("XMLUI", id, {"type":"window", "xml":self.__buildUI(self.data[profile])})

    def __sendMessage(self, answer, subject, message, data, recipient_list, id, profile):
        """Send actually the message
        @param subject: subject of the message
        @param message: body of the message
        @param data: data of the profile
        @param recipient_list: list of friends names, names are removed once message is sent
        @param id: id of the action
        @param profile: profile who launched the action
        """
        if answer:
            if not 'Here is a copy of the email that was sent' in answer:
                error(_("INTERNAL ERROR: no confirmation of message sent by CS, maybe the site has been modified ?"))
                #TODO: throw a warning to the frontend, saying that maybe the message has not been sent and to contact dev of this plugin
            #debug(_('HTML answer: %s') % answer)
        if recipient_list:
            recipient = recipient_list.pop()
            try:
                friend_id = data['friends'][recipient]['id']
            except KeyError:
                error('INTERNAL ERROR: unknown friend')
                return  #send an error to the frontend
            mess = message.replace('%name%',recipient).replace('%firstname%',recipient.split(' ')[0])
            info(_('Sending message to %s') % recipient)
            debug(_("\nsubject: %(subject)s\nmessage: \n---\n%(message)s\n---\n\n") % {'subject':subject,'message':mess})
            post_data = urllib.urlencode({'email[subject]':subject.encode('utf-8'),'email[body]':mess.encode('utf-8'),'email[id]':friend_id,'email[action]':'Send Message','email[replied_id]':'','email[couchsurf]':'','email[directions_to_add]':''})
            d = getPage("http://www.couchsurfing.org/send_message.html", method='POST', postdata=post_data, headers={'Content-Type':'application/x-www-form-urlencoded'} , agent=AGENT, cookies=data['cookies'])
            d.addCallback(self.__sendMessage, subject, message, data, recipient_list, id, profile)
            d.addErrback(self.erroCB, id)
        else:
            interface = XMLUI('window', title=_('Message sent')) #TODO: create particular actionResult for alerts ?
            interface.addText(_('The message has been sent to every recipients'))
            self.host.bridge.actionResult("XMLUI", id, {"type":"window", "xml":interface.toXml()})

    def sendMessage(self, id, data, profile):
        """Called to send a message to a friend
        @param data: dict with the following keys:
            friend: name of the recipient
            subject: subject of the message
            message: body of the message, with the following special keywords:
                - %name%: name of the friend
                - %firstname%: guessed first name of the friend (currently the first part of the name)
        """
        if not data['friends']:
            message_data={"reason": "bad data", "message":_(u"There is not recipient selected for this message !")}
            self.host.bridge.actionResult("ERROR", id, message_data)
            return
        friends = data['friends'].split('\t')
        subject = data['subject']
        message = data['message']
        info(_("sending message to %(friends)s with subject [%(subject)s]" % {'friends':friends, 'subject':subject}))
        self.__sendMessage(None, subject, message, self.data[profile], friends, id, profile)
     
    def __showUnreadMessages2(self, html, id, profile):
        """Called when the inbox page has been received"""
        #FIXME: that's really too fragile, only works if the unread messages are in the first page, and it would be too resources consuming for the website to DL each time all pages. In addition, the show attribute doesn't work as expected.
        soup = BeautifulSoup(html)
        for tag in soup.findAll(lambda tag: tag.name=='strong' and tag.a and tag.a['href'].startswith('messages.html?message_status=inbox')):
            link = "http://www.couchsurfing.org/"+str(tag.a['href'])
            webbrowser.open_new_tab(link) #TODO: the web browser need to already have CS cookies (i.e. already be opened & logged on CS, or be permanently loggued), a warning to the user should be sent/or a balloon-tip

    def showUnreadMessages(self, id, data, profile):
        """Called when user want to see all unread messages in the external browser"""
        d = getPage("http://www.couchsurfing.org/messages.html?message_status=inbox&show=10000", agent=AGENT, cookies=self.data[profile]['cookies'])
        d.addCallback(self.__showUnreadMessages2, id, profile)
        d.addErrback(self.erroCB, id)
        
