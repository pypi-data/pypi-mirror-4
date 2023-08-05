#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
SAT plugin for managing xep-0065

Copyright (C)
2002, 2003, 2004   Dave Smith (dizzyd@jabber.org)
2007, 2008         Fabio Forno (xmpp:ff@jabber.bluendo.com)
2009, 2010, 2011, 2012, 2013  Jérôme Poisson (goffi@goffi.org)

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

--

This program is based on proxy65 (http://code.google.com/p/proxy65),
originaly written by David Smith and modified by Fabio Forno.
It is sublicensed under GPL v3 (or any later version) as allowed by the original
license.

--

Here is a copy of the original license:

Copyright (C) 
2002-2004   Dave Smith (dizzyd@jabber.org)
2007-2008   Fabio Forno (xmpp:ff@jabber.bluendo.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from logging import debug, info, warning, error
from twisted.internet import protocol, reactor
from twisted.internet import error as jab_error
from twisted.words.protocols.jabber import jid, client as jabber_client
from twisted.protocols.basic import FileSender
from twisted.words.xish import domish
from twisted.web.client import getPage
from sat.core.exceptions import ProfileNotInCacheError
import struct
import hashlib

from zope.interface import implements

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

from wokkel import disco, iwokkel

IQ_SET = '/iq[@type="set"]'
NS_BS = 'http://jabber.org/protocol/bytestreams'
BS_REQUEST = IQ_SET + '/query[@xmlns="' + NS_BS + '"]'
TIMEOUT = 60 #timeout for workflow



PLUGIN_INFO = {
"name": "XEP 0065 Plugin",
"import_name": "XEP-0065",
"type": "XEP",
"protocols": ["XEP-0065"],
"main": "XEP_0065",
"handler": "yes",
"description": _("""Implementation of SOCKS5 Bytestreams""")
}

STATE_INITIAL = 0
STATE_AUTH    = 1
STATE_REQUEST = 2
STATE_READY   = 3
STATE_AUTH_USERPASS = 4
STATE_TARGET_INITIAL = 5
STATE_TARGET_AUTH    = 6
STATE_TARGET_REQUEST = 7
STATE_TARGET_READY   = 8
STATE_LAST    = 9

STATE_CONNECT_PENDING = STATE_LAST + 1

SOCKS5_VER = 0x05

ADDR_IPV4 = 0x01
ADDR_DOMAINNAME = 0x03
ADDR_IPV6 = 0x04

CMD_CONNECT = 0x01
CMD_BIND = 0x02
CMD_UDPASSOC = 0x03

AUTHMECH_ANON = 0x00
AUTHMECH_USERPASS = 0x02
AUTHMECH_INVALID = 0xFF

REPLY_SUCCESS = 0x00
REPLY_GENERAL_FAILUR = 0x01
REPLY_CONN_NOT_ALLOWED = 0x02
REPLY_NETWORK_UNREACHABLE = 0x03
REPLY_HOST_UNREACHABLE = 0x04
REPLY_CONN_REFUSED = 0x05
REPLY_TTL_EXPIRED = 0x06
REPLY_CMD_NOT_SUPPORTED = 0x07
REPLY_ADDR_NOT_SUPPORTED = 0x08


def calculateHash(from_jid, to_jid, sid):
    """Calculate SHA1 Hash according to XEP-0065
    @param from_jid: jid of the requester
    @param to_jid: jid of the target
    @param sid: session id
    @return: hash (string)"""
    return hashlib.sha1((sid + from_jid.full() + to_jid.full()).encode('utf-8')).hexdigest()



class SOCKSv5(protocol.Protocol, FileSender):
    def __init__(self):
        debug(_("Protocol init"))
        self.state = STATE_INITIAL
        self.buf = ""
        self.supportedAuthMechs = [ AUTHMECH_ANON ]
        self.supportedAddrs = [ ADDR_DOMAINNAME ]
        self.enabledCommands = [ CMD_CONNECT ]
        self.peersock = None
        self.addressType = 0
        self.requestType = 0

    def _startNegotiation(self):
        debug("_startNegotiation")
        self.state = STATE_TARGET_AUTH
        self.transport.write(struct.pack('!3B', SOCKS5_VER, 1, AUTHMECH_ANON))

    def _parseNegotiation(self):
        debug("_parseNegotiation")
        try:
            # Parse out data
            ver, nmethod = struct.unpack('!BB', self.buf[:2])
            methods = struct.unpack('%dB' % nmethod, self.buf[2:nmethod+2])

            # Ensure version is correct
            if ver != 5:
                self.transport.write(struct.pack('!BB', SOCKS5_VER, AUTHMECH_INVALID))
                self.transport.loseConnection()
                return

            # Trim off front of the buffer
            self.buf = self.buf[nmethod+2:]
            
            # Check for supported auth mechs
            for m in self.supportedAuthMechs:
                if m in methods:
                    # Update internal state, according to selected method
                    if m == AUTHMECH_ANON:
                        self.state = STATE_REQUEST
                    elif m == AUTHMECH_USERPASS:
                        self.state = STATE_AUTH_USERPASS
                    # Complete negotiation w/ this method
                    self.transport.write(struct.pack('!BB', SOCKS5_VER, m))
                    return

            # No supported mechs found, notify client and close the connection
            self.transport.write(struct.pack('!BB', SOCKS5_VER, AUTHMECH_INVALID))
            self.transport.loseConnection()
        except struct.error:
            pass

    def _parseUserPass(self):
        debug("_parseUserPass")
        try:
            # Parse out data
            ver, ulen = struct.unpack('BB', self.buf[:2])
            uname, = struct.unpack('%ds' % ulen, self.buf[2:ulen + 2])
            plen, = struct.unpack('B', self.buf[ulen + 2])
            password, = struct.unpack('%ds' % plen, self.buf[ulen + 3:ulen + 3 + plen])
            # Trim off fron of the buffer
            self.buf = self.buf[3 + ulen + plen:]
            # Fire event to authenticate user
            if self.authenticateUserPass(uname, password):
                # Signal success
                self.state = STATE_REQUEST
                self.transport.write(struct.pack('!BB', SOCKS5_VER, 0x00))
            else:
                # Signal failure
                self.transport.write(struct.pack('!BB', SOCKS5_VER, 0x01))
                self.transport.loseConnection()
        except struct.error:
            pass

    def sendErrorReply(self, errorcode):
        debug("sendErrorReply")
        # Any other address types are not supported
        result = struct.pack('!BBBBIH', SOCKS5_VER, errorcode, 0, 1, 0, 0)
        self.transport.write(result)
        self.transport.loseConnection()
    
    def _parseRequest(self):
        debug("_parseRequest")
        try:
            # Parse out data and trim buffer accordingly
            ver, cmd, rsvd, self.addressType = struct.unpack('!BBBB', self.buf[:4])

            # Ensure we actually support the requested address type
            if self.addressType not in self.supportedAddrs:
                self.sendErrorReply(REPLY_ADDR_NOT_SUPPORTED)
                return

            # Deal with addresses
            if self.addressType == ADDR_IPV4:
                addr, port = struct.unpack('!IH', self.buf[4:10])
                self.buf = self.buf[10:]
            elif self.addressType == ADDR_DOMAINNAME:            
                nlen = ord(self.buf[4])
                addr, port = struct.unpack('!%dsH' % nlen, self.buf[5:])
                self.buf = self.buf[7 + len(addr):]
            else:
                # Any other address types are not supported
                self.sendErrorReply(REPLY_ADDR_NOT_SUPPORTED)
                return

            # Ensure command is supported
            if cmd not in self.enabledCommands:
                # Send a not supported error
                self.sendErrorReply(REPLY_CMD_NOT_SUPPORTED)
                return

            # Process the command
            if cmd == CMD_CONNECT:
                self.connectRequested(addr, port)
            elif cmd == CMD_BIND:
                self.bindRequested(addr, port)
            else:
                # Any other command is not supported
                self.sendErrorReply(REPLY_CMD_NOT_SUPPORTED)

        except struct.error, why:
            return None

    def _makeRequest(self):
        debug("_makeRequest")
        self.state = STATE_TARGET_REQUEST
        sha1 = calculateHash(self.data["from"], self.data["to"], self.sid)
        request = struct.pack('!5B%dsH' % len(sha1), SOCKS5_VER, CMD_CONNECT, 0, ADDR_DOMAINNAME, len(sha1), sha1, 0)
        self.transport.write(request)

    def _parseRequestReply(self):
        debug("_parseRequestReply")
        try:
            ver, rep, rsvd, self.addressType = struct.unpack('!BBBB', self.buf[:4])
            # Ensure we actually support the requested address type
            if self.addressType not in self.supportedAddrs:
                self.sendErrorReply(REPLY_ADDR_NOT_SUPPORTED)
                return

            # Deal with addresses
            if self.addressType == ADDR_IPV4:
                addr, port = struct.unpack('!IH', self.buf[4:10])
                self.buf = self.buf[10:]
            elif self.addressType == ADDR_DOMAINNAME:            
                nlen = ord(self.buf[4])
                addr, port = struct.unpack('!%dsH' % nlen, self.buf[5:])
                self.buf = self.buf[7 + len(addr):]
            else:
                # Any other address types are not supported
                self.sendErrorReply(REPLY_ADDR_NOT_SUPPORTED)
                return

            # Ensure reply is OK
            if rep != REPLY_SUCCESS:
                self.loseConnection()
                return

            if self.factory.proxy:
                self.state = STATE_READY
                self.factory.activateCb(self.sid, self.factory.iq_id, self.startTransfer, self.profile)
            else:
                self.state = STATE_TARGET_READY
                self.factory.activateCb(self.sid, self.factory.iq_id, self.profile)

        except struct.error, why:
            return None

    def connectionMade(self):
        debug("connectionMade (mode = %s)" % "requester" if isinstance(self.factory, Socks5ServerFactory) else "target")
        
        if isinstance(self.factory, Socks5ClientFactory):
            self.sid = self.factory.sid
            self.profile = self.factory.profile
            self.data = self.factory.data
            self.state = STATE_TARGET_INITIAL
            self._startNegotiation()

    def connectRequested(self, addr, port):
        debug("connectRequested")
        
        # Check that this session is expected
        if not self.factory.hash_sid_map.has_key(addr):
            #no: we refuse it
            self.sendErrorReply(REPLY_CONN_REFUSED)
            return
        self.sid, self.profile = self.factory.hash_sid_map[addr]
        client = self.factory.host.getClient(self.profile)
        if not client:
            raise ProfileNotInCacheError
        client.xep_0065_current_stream[self.sid]["start_transfer_cb"] = self.startTransfer
        self.connectCompleted(addr, 0)
        self.transport.stopReading()

    def startTransfer(self, file_obj):
        """Callback called when the result iq is received"""
        d = self.beginFileTransfer(file_obj, self.transport)
        d.addCallback(self.fileTransfered)
    
    def fileTransfered(self, d):
        info(_("File transfer completed, closing connection"))
        self.transport.loseConnection()
        self.factory.finishedCb(self.sid, True, self.profile)

    def connectCompleted(self, remotehost, remoteport):
        debug("connectCompleted")
        if self.addressType == ADDR_IPV4:
            result = struct.pack('!BBBBIH', SOCKS5_VER, REPLY_SUCCESS, 0, 1, remotehost, remoteport)
        elif self.addressType == ADDR_DOMAINNAME:
            result = struct.pack('!BBBBB%dsH' % len(remotehost), SOCKS5_VER, REPLY_SUCCESS, 0,
                                 ADDR_DOMAINNAME, len(remotehost), remotehost, remoteport)
        self.transport.write(result)
        self.state = STATE_READY
    
    def bindRequested(self, addr, port):
        pass
    
    def authenticateUserPass(self, user, passwd):
        debug("User/pass: %s/%s", user, passwd)
        return True

    def dataReceived(self, buf):
        if self.state == STATE_TARGET_READY:
            self.data["file_obj"].write(buf)
            return

        self.buf = self.buf + buf
        if self.state == STATE_INITIAL:
            self._parseNegotiation()
        if self.state == STATE_AUTH_USERPASS:
            self._parseUserPass()
        if self.state == STATE_REQUEST:
            self._parseRequest()
        if self.state == STATE_TARGET_AUTH:
            ver, method = struct.unpack('!BB', buf)
            self.buf = self.buf[2:]
            if ver!=SOCKS5_VER or method!=AUTHMECH_ANON:
                self.transport.loseConnection()
            else:
                self._makeRequest()
        if self.state == STATE_TARGET_REQUEST:
            self._parseRequestReply()


    def clientConnectionLost(self, reason):
        debug("clientConnectionLost")
        self.transport.loseConnection()

    def connectionLost(self, reason):
        debug("connectionLost")
        if self.state != STATE_CONNECT_PENDING:
            self.transport.unregisterProducer()
            if self.peersock != None:
                self.peersock.peersock = None
                self.peersock.transport.unregisterProducer()
                self.peersock = None


class Socks5ServerFactory(protocol.ServerFactory):
    protocol = SOCKSv5

    def __init__(self, host, hash_sid_map, finishedCb):
        self.host = host
        self.hash_sid_map = hash_sid_map
        self.finishedCb = finishedCb

    def startedConnecting(self, connector):
        debug (_("Socks 5 server connection started"))

    def clientConnectionLost(self, connector, reason):
        debug (_("Socks 5 server connection lost (reason: %s)"), reason)

class Socks5ClientFactory(protocol.ClientFactory):
    protocol = SOCKSv5

    def __init__(self, current_stream, sid, iq_id, activateCb, finishedCb, proxy=False, profile=None):
        """Init the Client Factory
        @param current_stream: current streams data
        @param sid: Session ID
        @param iq_id: iq id used to initiate the stream
        @param activateCb: method to call to activate the stream
        @param finishedCb: method to call when the stream session is finished
        @param proxy: True if we are connecting throught a proxy (and we are a requester)
        @param profile: %(doc_profile)s"""
        assert(profile)
        self.data = current_stream[sid]
        self.sid = sid
        self.iq_id = iq_id
        self.activateCb = activateCb
        self.finishedCb = finishedCb
        self.proxy = proxy
        self.profile = profile

    def startedConnecting(self, connector):
        debug (_("Socks 5 client connection started"))

    def clientConnectionLost(self, connector, reason):
        debug (_("Socks 5 client connection lost (reason: %s)"), reason)
        self.finishedCb(self.sid, reason.type == jab_error.ConnectionDone, self.profile) #TODO: really check if the state is actually successful


class XEP_0065():
    
    NAMESPACE = NS_BS

    params = """
    <params>
    <general>
    <category name="File Transfer">
        <param name="IP" value='0.0.0.0' default_cb='yes' type="string" />
        <param name="Port" value="28915" type="string" />
    </category>
    </general>
    <individual>
    <category name="File Transfer">
        <param name="Proxy" value="" type="string" />
        <param name="Proxy host" value="" type="string" />
        <param name="Proxy port" value="" type="string" />
    </category>
    </individual>
    </params>
    """

    def __init__(self, host):
        info(_("Plugin XEP_0065 initialization"))
        
        #session data
        self.hash_sid_map = {}  #key: hash of the transfer session, value: (session id, profile)
        
        self.host = host
        debug(_("registering"))
        self.server_factory = Socks5ServerFactory(host, self.hash_sid_map, lambda sid, success, profile: self._killId(sid, success, profile=profile))

        #parameters
        host.memory.importParams(XEP_0065.params)
        host.memory.setDefault("IP", "File Transfer", self.getExternalIP)
        port = int(self.host.memory.getParamA("Port", "File Transfer"))
        
        info(_("Launching Socks5 Stream server on port %d"), port)
        reactor.listenTCP(port, self.server_factory)
    
    def getHandler(self, profile):
        return XEP_0065_handler(self)  
   
    def profileConnected(self, profile):
        client = self.host.getClient(profile)
        if not client:
            raise ProfileNotInCacheError
        client.xep_0065_current_stream = {} #key: stream_id, value: data(dict)

    def getExternalIP(self):
        """Return IP visible from outside, by asking to a website"""
        return getPage("http://www.goffi.org/sat_tools/get_ip.php")

    def getProgress(self, sid, data, profile):
        """Fill data with position of current transfer"""
        client = self.host.getClient(profile)
        if not client:
            raise ProfileNotInCacheError
        try:
            file_obj = client.xep_0065_current_stream[sid]["file_obj"]
            data["position"] = str(file_obj.tell())
            data["size"] = str(client.xep_0065_current_stream[sid]["size"])
        except:
            pass
    
    def _timeOut(self, sid, profile):
        """Delecte current_stream id, called after timeout
        @param id: id of client.xep_0065_current_stream"""
        info(_("Socks5 Bytestream: TimeOut reached for id %s [%s]") % (sid, profile));
        self._killId(sid, False, "TIMEOUT", profile)
    
    def _killId(self, sid, success=False, failure_reason="UNKNOWN", profile=None):
        """Delete an current_stream id, clean up associated observers
        @param sid: id of client.xep_0065_current_stream"""
        assert(profile)
        client = self.host.getClient(profile)
        if not client:
            warning(_("Client no more in cache"))
            return
        if not client.xep_0065_current_stream.has_key(sid):
            warning(_("kill id called on a non existant id"))
            return
        if client.xep_0065_current_stream[sid].has_key("observer_cb"):
            xmlstream = client.xep_0065_current_stream[sid]["xmlstream"]
            xmlstream.removeObserver(client.xep_0065_current_stream[sid]["event_data"], client.xep_0065_current_stream[sid]["observer_cb"])
        if client.xep_0065_current_stream[sid]['timer'].active():
            client.xep_0065_current_stream[sid]['timer'].cancel()
        if client.xep_0065_current_stream[sid].has_key("size"):
            self.host.removeProgressCB(sid, profile)
       
        file_obj = client.xep_0065_current_stream[sid]['file_obj']
        success_cb = client.xep_0065_current_stream[sid]['success_cb']
        failure_cb = client.xep_0065_current_stream[sid]['failure_cb']
        
        session_hash = client.xep_0065_current_stream[sid].get('hash')
        del client.xep_0065_current_stream[sid]
        if session_hash in self.hash_sid_map:
            #FIXME: check that self.hash_sid_map is correctly cleaned in all cases (timeout, normal flow, etc).
            del self.hash_sid_map[session_hash]

        if success:
            success_cb(sid, file_obj, NS_BS, profile)
        else:
            failure_cb(sid, file_obj, NS_BS, failure_reason, profile)

    def startStream(self, file_obj, to_jid, sid, length, successCb, failureCb, size = None, profile=None):
        """Launch the stream workflow
        @param file_obj: file_obj to send
        @param to_jid: JID of the recipient
        @param sid: Stream session id
        @param length: number of byte to send, or None to send until the end
        @param successCb: method to call when stream successfuly finished
        @param failureCb: method to call when something goes wrong
        @param profile: %(doc_profile)s"""
        assert(profile)
        client = self.host.getClient(profile)
        if not client:
            error(_("Unknown profile, this should not happen"))
            raise ProfileNotInCacheError
        
        if length != None:
            error(_('stream length not managed yet'))
            return;
        
        profile_jid = client.jid
        xmlstream = client.xmlstream
        
        data = client.xep_0065_current_stream[sid] = {}
        data["timer"] = reactor.callLater(TIMEOUT, self._timeOut, sid, profile)
        data["file_obj"] = file_obj
        data["from"] = profile_jid
        data["to"] = to_jid
        data["success_cb"] = successCb
        data["failure_cb"] = failureCb
        data["xmlstream"] = xmlstream
        data["hash"] = calculateHash(profile_jid, to_jid, sid)
        self.hash_sid_map[data["hash"]] = (sid, profile)
        if size:
            data["size"] = size
            self.host.registerProgressCB(sid, self.getProgress, profile)
        iq_elt = jabber_client.IQ(xmlstream,'set')
        iq_elt["from"] = profile_jid.full()
        iq_elt["to"] = to_jid.full()
        query_elt = iq_elt.addElement('query', NS_BS)
        query_elt['mode'] = 'tcp'
        query_elt['sid'] = sid
        #first streamhost: direct connection
        streamhost = query_elt.addElement('streamhost')
        streamhost['host'] = self.host.memory.getParamA("IP", "File Transfer")
        streamhost['port'] = self.host.memory.getParamA("Port", "File Transfer")
        streamhost['jid'] = profile_jid.full()

        #second streamhost: mediated connection, using proxy
        streamhost = query_elt.addElement('streamhost')
        streamhost['host'] = self.host.memory.getParamA("Proxy host", "File Transfer", profile_key=profile)
        streamhost['port'] = self.host.memory.getParamA("Proxy port", "File Transfer", profile_key=profile)
        streamhost['jid'] = self.host.memory.getParamA("Proxy", "File Transfer", profile_key=profile)

        iq_elt.addCallback(self.iqResult, sid, profile)
        iq_elt.send()

    def iqResult(self, sid, profile, iq_elt):
        """Called when the result of open iq is received"""
        if iq_elt["type"] == "error":
            warning(_("Transfer failed"))
            return
        client = self.host.getClient(profile)
        if not client:
            raise ProfileNotInCacheError
        try:
            data = client.xep_0065_current_stream[sid]
            file_obj = data["file_obj"]
            timer = data["timer"]
        except KeyError:
            error(_("Internal error, can't do transfer"))
            return
        
        if timer.active():
            timer.cancel()
        
        profile_jid, xmlstream = self.host.getJidNStream(profile)
        query_elt = iq_elt.firstChildElement()
        streamhost_elts = filter(lambda elt: elt.name == 'streamhost-used', query_elt.elements())
        if not streamhost_elts:
            warning(_("No streamhost found in stream query"))
            return

        streamhost_jid = streamhost_elts[0]['jid']
        if streamhost_jid != profile_jid.full():
            debug(_("A proxy server is used"))
            proxy_host = self.host.memory.getParamA("Proxy host", "File Transfer", profile_key=profile)
            proxy_port = self.host.memory.getParamA("Proxy port", "File Transfer", profile_key=profile)
            proxy_jid = self.host.memory.getParamA("Proxy", "File Transfer", profile_key=profile)
            if proxy_jid != streamhost_jid:
                warning(_("Proxy jid is not the same as in parameters, this should not happen"))
                return
            factory = Socks5ClientFactory(client.xep_0065_current_stream, sid, None, self.activateProxyStream, lambda sid, success, profile: self._killId(sid, success, profile=profile), True, profile)
            reactor.connectTCP(proxy_host, int(proxy_port), factory)
        else:
            data["start_transfer_cb"](file_obj) #We now activate the stream

    def activateProxyStream(self, sid, iq_id, start_transfer_cb, profile):
        debug(_("activating stream"))
        client = self.host.getClient(profile)
        if not client:
            raise ProfileNotInCacheError
        data = client.xep_0065_current_stream[sid]
        profile_jid, xmlstream = self.host.getJidNStream(profile)

        iq_elt = client.IQ(xmlstream,'set')
        iq_elt["from"] = profile_jid.full()
        iq_elt["to"] = self.host.memory.getParamA("Proxy", "File Transfer", profile_key=profile)
        query_elt = iq_elt.addElement('query', NS_BS)
        query_elt['sid'] = sid
        query_elt.addElement('activate', content=data['to'].full())
        iq_elt.addCallback(self.proxyResult, sid, start_transfer_cb, data['file_obj'])
        iq_elt.send()

    def proxyResult(self, sid, start_transfer_cb, file_obj, iq_elt):
        if iq_elt['type'] == 'error':
            warning(_("Can't activate the proxy stream"))
            return
        else:
            start_transfer_cb(file_obj)

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
        data = client.xep_0065_current_stream[sid] = {}
        data["from"] = from_jid
        data["file_obj"] = file_obj
        data["seq"] = -1
        if size:
            data["size"] = size
            self.host.registerProgressCB(sid, self.getProgress, profile)
        data["timer"] = reactor.callLater(TIMEOUT, self._timeOut, sid, profile)
        data["success_cb"] = success_cb
        data["failure_cb"] = failure_cb
    
    
    def streamQuery(self, iq_elt, profile):
        """Get file using byte stream"""
        debug(_("BS stream query"))
        client = self.host.getClient(profile)
        
        if not client:
            raise ProfileNotInCacheError
        
        xmlstream = client.xmlstream

        iq_elt.handled = True
        query_elt = iq_elt.firstChildElement()
        sid = query_elt.getAttribute("sid")
        streamhost_elts = filter(lambda elt: elt.name == 'streamhost', query_elt.elements())
        
        if not sid in client.xep_0065_current_stream:
            warning(_("Ignoring unexpected BS transfer: %s" % sid))
            self.sendNotAcceptableError(iq_elt['id'], iq_elt['from'], xmlstream)
            return

        client.xep_0065_current_stream[sid]['timer'].cancel()
        client.xep_0065_current_stream[sid]["to"] = jid.JID(iq_elt["to"])
        client.xep_0065_current_stream[sid]["xmlstream"] = xmlstream

        if not streamhost_elts:
            warning(_("No streamhost found in stream query %s" % sid))
            self.sendBadRequestError(iq_elt['id'], iq_elt['from'], xmlstream)
            return

        streamhost_elt = streamhost_elts[0] #TODO: manage several streamhost elements case
        sh_host = streamhost_elt.getAttribute("host")
        sh_port = streamhost_elt.getAttribute("port")
        sh_jid = streamhost_elt.getAttribute("jid")
        if not sh_host or not sh_port or not sh_jid:
            warning(_("incomplete streamhost element"))
            self.sendBadRequestError(iq_elt['id'], iq_elt['from'], xmlstream)
            return

        client.xep_0065_current_stream[sid]["streamhost"] = (sh_host, sh_port, sh_jid)

        info (_("Stream proposed: host=[%(host)s] port=[%(port)s]") % {'host':sh_host, 'port':sh_port})
        factory = Socks5ClientFactory(client.xep_0065_current_stream, sid, iq_elt["id"], self.activateStream, lambda sid, success, profile: self._killId(sid, success, profile=profile), profile=profile)
        reactor.connectTCP(sh_host, int(sh_port), factory)
                
    def activateStream(self, sid, iq_id, profile):
        client = self.host.getClient(profile)
        if not client:
            raise ProfileNotInCacheError
        debug(_("activating stream"))
        result = domish.Element((None, 'iq'))
        data = client.xep_0065_current_stream[sid]
        result['type'] = 'result'
        result['id'] = iq_id
        result['from'] = data["to"].full()
        result['to'] = data["from"].full()
        query = result.addElement('query', NS_BS)
        query['sid'] = sid
        streamhost = query.addElement('streamhost-used')
        streamhost['jid'] = data["streamhost"][2]
        data["xmlstream"].send(result)

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
        error_el['type'] = 'modify'
        error_el.addElement(('urn:ietf:params:xml:ns:xmpp-stanzas','not-acceptable'))
        xmlstream.send(result)

    def sendBadRequestError(self, iq_id, to_jid, xmlstream):
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
        error_el.addElement(('urn:ietf:params:xml:ns:xmpp-stanzas','bad-request'))
        xmlstream.send(result)

class XEP_0065_handler(XMPPHandler):
    implements(iwokkel.IDisco)
    
    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host

    def _proxyDataResult(self, iq_elt):
        """Called with the informations about proxy according to XEP-0065 #4
        Params should be filled with these infos"""
        if iq_elt["type"] == "error":
            warning(_("Can't determine proxy informations"))
            return
        query_elt = iq_elt.firstChildElement()
        if query_elt.name != "query":
            warning(_("Bad answer received from proxy"))
            return
        streamhost_elts = filter(lambda elt: elt.name == 'streamhost', query_elt.elements())
        if not streamhost_elts:
            warning(_("No streamhost found in stream query"))
            return
        if len(streamhost_elts) != 1:
            warning(_("Multiple streamhost elements in proxy not managed, keeping only the first one"))
        streamhost_elt = streamhost_elts[0]
        proxy = self.host.memory.setParam("Proxy", streamhost_elt.getAttribute("jid",""), "File Transfer", self.parent.profile)
        proxy = self.host.memory.setParam("Proxy host", streamhost_elt.getAttribute("host",""), "File Transfer", self.parent.profile)
        proxy = self.host.memory.setParam("Proxy port", streamhost_elt.getAttribute("port",""), "File Transfer", self.parent.profile)

    
    def connectionInitialized(self):
        def after_init(ignore):
            proxy_ent = self.host.memory.getServerServiceEntity("proxy", "bytestreams", self.parent.profile)
            if not proxy_ent:
                debug(_("No proxy found on this server"))
                return
            iq_elt = jabber_client.IQ(self.parent.xmlstream,'get')
            iq_elt["to"] = proxy_ent.full()
            query_elt = iq_elt.addElement('query', NS_BS)
            iq_elt.addCallback(self._proxyDataResult)
            iq_elt.send()


        self.xmlstream.addObserver(BS_REQUEST, self.plugin_parent.streamQuery, profile = self.parent.profile)
        proxy = self.host.memory.getParamA("Proxy", "File Transfer", profile_key = self.parent.profile)
        if not proxy:
            self.parent.client_initialized.addCallback(after_init)
            


    def getDiscoInfo(self, requestor, target, nodeIdentifier=''):
        return [disco.DiscoFeature(NS_BS)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=''):
        return []
