#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SAT plugin for managing gateways (xep-0047)
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
from twisted.words.protocols.jabber import client as jabber_client, jid
from twisted.words.xish import domish
import twisted.internet.error
from twisted.internet import reactor
from sat.core.exceptions import ProfileNotInCacheError

from wokkel import disco, iwokkel

from zope.interface import implements

import base64

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

MESSAGE = '/message'
IQ_SET = '/iq[@type="set"]'
NS_IBB = 'http://jabber.org/protocol/ibb'
IBB_OPEN = IQ_SET + '/open[@xmlns="' + NS_IBB + '"]'
IBB_CLOSE = IQ_SET + '/close[@xmlns="' + NS_IBB + '" and @sid="%s"]'
IBB_IQ_DATA = IQ_SET + '/data[@xmlns="' + NS_IBB + '" and @sid="%s"]'
IBB_MESSAGE_DATA = MESSAGE + '/data[@xmlns="' + NS_IBB + '" and @sid="%s"]'
TIMEOUT = 60 #timeout for workflow
BLOCK_SIZE = 4096

PLUGIN_INFO = {
"name": "In-Band Bytestream Plugin",
"import_name": "XEP-0047",
"type": "XEP",
"protocols": ["XEP-0047"],
"main": "XEP_0047",
"handler": "yes",
"description": _("""Implementation of In-Band Bytestreams""")
}

class XEP_0047():
    NAMESPACE = NS_IBB

    def __init__(self, host):
        info(_("In-Band Bytestreams plugin initialization"))
        self.host = host

    def getHandler(self, profile):
        return XEP_0047_handler(self)

    def profileConnected(self, profile):
        client = self.host.getClient(profile)
        if not client:
            raise ProfileNotInCacheError
        client.xep_0047_current_stream = {} #key: stream_id, value: data(dict)
    
    def _timeOut(self, sid, profile):
        """Delecte current_stream id, called after timeout
        @param id: id of client.xep_0047_current_stream"""
        info(_("In-Band Bytestream: TimeOut reached for id %s [%s]") % (sid, profile));
        self._killId(sid, False, "TIMEOUT", profile)
    
    def _killId(self, sid, success=False, failure_reason="UNKNOWN", profile=None):
        """Delete an current_stream id, clean up associated observers
        @param sid: id of client.xep_0047_current_stream"""
        assert(profile)
        client = self.host.getClient(profile)
        if not client:
            warning(_("Client no more in cache"))
            return
        if not client.xep_0047_current_stream.has_key(sid):
            warning(_("kill id called on a non existant id"))
            return
        if client.xep_0047_current_stream[sid].has_key("observer_cb"):
            client.xmlstream.removeObserver(client.xep_0047_current_stream[sid]["event_data"], client.xep_0047_current_stream[sid]["observer_cb"])
        if client.xep_0047_current_stream[sid]['timer'].active():
            client.xep_0047_current_stream[sid]['timer'].cancel()
        if client.xep_0047_current_stream[sid].has_key("size"):
            self.host.removeProgressCB(sid, profile)
       
        file_obj = client.xep_0047_current_stream[sid]['file_obj']
        success_cb = client.xep_0047_current_stream[sid]['success_cb']
        failure_cb = client.xep_0047_current_stream[sid]['failure_cb']
        
        del client.xep_0047_current_stream[sid]

        if success:
            success_cb(sid, file_obj, NS_IBB, profile)
        else:
            failure_cb(sid, file_obj, NS_IBB, failure_reason, profile)
    
    def getProgress(self, sid, data, profile):
        """Fill data with position of current transfer"""
        client = self.host.getClient(profile)
        if not client:
            raise ProfileNotInCacheError
        try:
            file_obj = client.xep_0047_current_stream[sid]["file_obj"]
            data["position"] = str(file_obj.tell())
            data["size"] = str(client.xep_0047_current_stream[sid]["size"])
        except:
            pass
    
    def prepareToReceive(self, from_jid, sid, file_obj, size, success_cb, failure_cb, profile):
        """Called when a bytestream is imminent
        @param from_jid: jid of the sender
        @param sid: Stream id
        @param file_obj: File object where data will be written
        @param size: full size of the data, or None if unknown
        @param success_cb: method to call when successfuly finished
        @param failure_cb: method to call when something goes wrong
        @param profile: %(doc_profile)s"""
        client = self.host.getClient(profile)
        if not client:
            raise ProfileNotInCacheError
        data = client.xep_0047_current_stream[sid] = {}
        data["from"] = from_jid
        data["file_obj"] = file_obj
        data["seq"] = -1
        if size:
            data["size"] = size
            self.host.registerProgressCB(sid, self.getProgress, profile)
        data["timer"] = reactor.callLater(TIMEOUT, self._timeOut, sid)
        data["success_cb"] = success_cb
        data["failure_cb"] = failure_cb

    def streamOpening(self, IQ, profile):
        debug(_("IBB stream opening"))
        IQ.handled=True
        client = self.host.getClient(profile)
        if not client:
            raise ProfileNotInCacheError
        open_elt = IQ.firstChildElement()
        block_size = open_elt.getAttribute('block-size')
        sid = open_elt.getAttribute('sid')
        stanza = open_elt.getAttribute('stanza', 'iq')
        if not sid or not block_size or int(block_size)>65535:
            warning(_("malformed IBB transfer: %s" % IQ['id']))
            self.sendNotAcceptableError(IQ['id'], IQ['from'], client.xmlstream)
            return
        if not sid in client.xep_0047_current_stream:
            warning(_("Ignoring unexpected IBB transfer: %s" % sid))
            self.sendNotAcceptableError(IQ['id'], IQ['from'], client.xmlstream)
            return
        if client.xep_0047_current_stream[sid]["from"] != jid.JID(IQ['from']):
            warning(_("sended jid inconsistency (man in the middle attack attempt ?)"))
            self.sendNotAcceptableError(IQ['id'], IQ['from'], client.xmlstream)
            self._killId(sid, False, "PROTOCOL_ERROR", profile=profile)
            return

        #at this stage, the session looks ok and will be accepted

        #we reset the timeout:
        client.xep_0047_current_stream[sid]["timer"].reset(TIMEOUT)

        #we save the xmlstream, events and observer data to allow observer removal
        client.xep_0047_current_stream[sid]["event_data"] = event_data = (IBB_MESSAGE_DATA if stanza=='message' else IBB_IQ_DATA) % sid
        client.xep_0047_current_stream[sid]["observer_cb"] = observer_cb = self.messageData if stanza=='message' else self.iqData 
        event_close = IBB_CLOSE % sid
        #we now set the stream observer to look after data packet
        client.xmlstream.addObserver(event_data, observer_cb, profile = profile)
        client.xmlstream.addOnetimeObserver(event_close, self.streamClosing, profile = profile)
        #finally, we send the accept stanza
        result = domish.Element((None, 'iq'))
        result['type'] = 'result'
        result['id'] = IQ['id']
        result['to'] = IQ['from']
        client.xmlstream.send(result)

    def streamClosing(self, IQ, profile):
        IQ.handled=True
        client = self.host.getClient(profile)
        if not client:
            raise ProfileNotInCacheError
        debug(_("IBB stream closing"))
        data_elt = IQ.firstChildElement()
        sid = data_elt.getAttribute('sid')
        result = domish.Element((None, 'iq'))
        result['type'] = 'result'
        result['id'] = IQ['id']
        result['to'] = IQ['from']
        client.xmlstream.send(result)
        self._killId(sid, success=True, profile=profile)

    def iqData(self, IQ, profile):
        IQ.handled=True
        client = self.host.getClient(profile)
        if not client:
            raise ProfileNotInCacheError
        data_elt = IQ.firstChildElement()
        
        if self._manageDataElt(data_elt, 'iq', IQ['id'], jid.JID(IQ['from']), profile):
            #and send a success answer
            result = domish.Element((None, 'iq'))
            result['type'] = 'result'
            result['id'] = IQ['id']
            result['to'] = IQ['from']
            
            client.xmlstream.send(result)
   
    def messageData(self, message_elt, profile):
        data_elt = message_elt.firstChildElement()
        sid = message_elt.getAttribute('id','')
        self._manageDataElt(message_elt, 'message', sid, jid.JID(message_elt['from']), profile)

    def _manageDataElt(self, data_elt, stanza, sid, stanza_from_jid, profile):
        """Manage the data elelement (check validity and write to the file_obj)
        @param data_elt: "data" domish element
        @return: True if success"""
        client = self.host.getClient(profile)
        if not client:
            raise ProfileNotInCacheError
        sid = data_elt.getAttribute('sid')
        if sid not in client.xep_0047_current_stream:
            error(_("Received data for an unknown session id"))
            return False

        from_jid = client.xep_0047_current_stream[sid]["from"]
        file_obj = client.xep_0047_current_stream[sid]["file_obj"]

        if stanza_from_jid != from_jid:
            warning(_("sended jid inconsistency (man in the middle attack attempt ?)"))
            if stanza=='iq':
                self.sendNotAcceptableError(sid, from_jid, client.xmlstream)
            return False

        client.xep_0047_current_stream[sid]["seq"]+=1
        if int(data_elt.getAttribute("seq",-1)) != client.xep_0047_current_stream[sid]["seq"]:
            warning(_("Sequence error"))
            if stanza=='iq':
                self.sendNotAcceptableError(data_elt["id"], from_jid, client.xmlstream)
            return False

        #we reset the timeout:
        client.xep_0047_current_stream[sid]["timer"].reset(TIMEOUT)

        #we can now decode the data
        try:
            file_obj.write(base64.b64decode(str(data_elt)))
        except TypeError:
            #The base64 data is invalid
            warning(_("Invalid base64 data"))
            if stanza=='iq':
                self.sendNotAcceptableError(data_elt["id"], from_jid, client.xmlstream)
            return False
        return True

    def sendNotAcceptableError(self, iq_id, to_jid, xmlstream):
        """Not acceptable error used when the stream is not expected or something is going wrong
        @param iq_id: IQ id
        @param to_jid: addressee
        @param xmlstream: XML stream to use to send the error"""
        result = domish.Element((None, 'iq'))
        result['type'] = 'result'
        result['id'] = iq_id
        result['to'] = to_jid 
        error_el = result.addElement('error')
        error_el['type'] = 'cancel'
        error_el.addElement(('urn:ietf:params:xml:ns:xmpp-stanzas','not-acceptable'))
        xmlstream.send(result)

    def startStream(self, file_obj, to_jid, sid, length, successCb, failureCb, size = None, profile=None):
        """Launch the stream workflow
        @param file_obj: file_obj to send
        @param to_jid: JID of the recipient
        @param sid: Stream session id
        @param length: number of byte to send, or None to send until the end
        @param successCb: method to call when stream successfuly finished
        @param failureCb: method to call when something goes wrong
        @param profile: %(doc_profile)s"""
        client = self.host.getClient(profile)
        if not client:
            raise ProfileNotInCacheError
        if length != None:
            error(_('stream length not managed yet'))
            return;
        data = client.xep_0047_current_stream[sid] = {}
        data["timer"] = reactor.callLater(TIMEOUT, self._timeOut, sid)
        data["file_obj"] = file_obj
        data["to"] = to_jid
        data["success_cb"] = successCb
        data["failure_cb"] = failureCb
        data["block_size"] = BLOCK_SIZE
        if size:
            data["size"] = size
            self.host.registerProgressCB(sid, self.getProgress, profile)
        iq_elt = jabber_client.IQ(client.xmlstream,'set')
        iq_elt['from'] = client.jid.full()
        iq_elt['to'] = to_jid.full()
        open_elt = iq_elt.addElement('open',NS_IBB)
        open_elt['block-size'] = str(BLOCK_SIZE)
        open_elt['sid'] = sid
        open_elt['stanza'] = 'iq'
        iq_elt.addCallback(self.iqResult, sid, 0, length, profile)
        iq_elt.send()

    def iqResult(self, sid, seq, length, profile, iq_elt):
        """Called when the result of open iq is received"""
        client = self.host.getClient(profile)
        if not client:
            raise ProfileNotInCacheError
        data = client.xep_0047_current_stream[sid]
        if iq_elt["type"] == "error":
            warning(_("Transfer failed"))
            self.terminateStream(sid, "IQ_ERROR")
            return
        
        if data['timer'].active():
            data['timer'].cancel()
        
        buffer = data["file_obj"].read(data["block_size"])
        if buffer:
            next_iq_elt = jabber_client.IQ(client.xmlstream,'set')
            next_iq_elt['to'] = data["to"].full()
            data_elt = next_iq_elt.addElement('data', NS_IBB)
            data_elt['seq'] = str(seq)
            data_elt['sid'] = sid
            data_elt.addContent(base64.b64encode(buffer))
            next_iq_elt.addCallback(self.iqResult, sid, seq+1, length, profile)
            next_iq_elt.send()
        else:
            self.terminateStream(sid, profile=profile)

    def terminateStream(self, sid, failure_reason = None, profile=None):
        """Terminate the stream session
        @param to_jid: recipient
        @param sid: Session id
        @param file_obj: file object used
        @param xmlstream: XML stream used with this session
        @param progress_cb: True if we have to remove the progress callback
        @param callback: method to call after finishing
        @param failure_reason: reason of the failure, or None if steam was successful"""
        client = self.host.getClient(profile)
        if not client:
            raise ProfileNotInCacheError
        data = client.xep_0047_current_stream[sid]
        iq_elt = jabber_client.IQ(client.xmlstream,'set')
        iq_elt['to'] = data["to"].full()
        close_elt = iq_elt.addElement('close',NS_IBB)
        close_elt['sid'] = sid
        iq_elt.send()
        self.host.removeProgressCB(sid, profile)
        if failure_reason:
            self._killId(sid, False, failure_reason, profile=profile)
        else:
            self._killId(sid, True, profile=profile)

class XEP_0047_handler(XMPPHandler):
    implements(iwokkel.IDisco)
    
    def __init__(self,parent):
        self.plugin_parent = parent
    
    def connectionInitialized(self):
        self.xmlstream.addObserver(IBB_OPEN, self.plugin_parent.streamOpening, profile = self.parent.profile)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=''):
        return [disco.DiscoFeature(NS_IBB)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=''):
        return []
