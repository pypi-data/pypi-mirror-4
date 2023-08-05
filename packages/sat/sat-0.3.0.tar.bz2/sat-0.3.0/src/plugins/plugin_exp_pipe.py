#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SAT plugin for managing pipes (experimental)
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
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber import error as jab_error
import os, os.path
from twisted.internet import reactor
from sat.core.exceptions import ProfileNotInCacheError

from wokkel import data_form

IQ_SET = '/iq[@type="set"]'
PROFILE_NAME = "pipe-transfer"
PROFILE = "http://jabber.org/protocol/si/profile/" + PROFILE_NAME

PLUGIN_INFO = {
"name": "Pipe Plugin",
"import_name": "EXP-PIPE",
"type": "EXP",
"protocols": ["EXP-PIPE"],
"dependencies": ["XEP-0020", "XEP-0095", "XEP-0065", "XEP-0047"],
"main": "Exp_Pipe",
"handler": "no",
"description": _("""Implementation of SI Pipe Transfer""")
}

class Exp_Pipe():
    """This is a modified version of XEP-0096 to work with named pipes instead of files"""

    def __init__(self, host):
        info(_("Plugin Pipe initialization"))
        self.host = host
        self.managed_stream_m = [self.host.plugins["XEP-0065"].NAMESPACE,
                                 self.host.plugins["XEP-0047"].NAMESPACE] #Stream methods managed
        self.host.plugins["XEP-0095"].registerSIProfile(PROFILE_NAME, self.transferRequest)
        host.bridge.addMethod("pipeOut", ".plugin", in_sign='ssa{ss}s', out_sign='s', method=self.pipeOut)

    def profileConnected(self, profile):
        client = self.host.getClient(profile)
        client._pipe_waiting_for_approval = {} #key = id, value = [transfer data, IdelayedCall Reactor timeout, 
                                        # current stream method, [failed stream methods], profile]
    
    def _kill_id(self, approval_id, profile):
        """Delete a waiting_for_approval id, called after timeout
        @param approval_id: id of _pipe_waiting_for_approval"""
        info(_("SI Pipe Transfer: TimeOut reached for id %s") % approval_id);
        try:
            client = self.host.getClient(profile)
            del client._pipe_waiting_for_approval[approval_id]
        except KeyError:
            warning(_("kill id called on a non existant approval id"))
    
    def transferRequest(self, iq_id, from_jid, si_id, si_mime_type, si_el, profile):
        """Called when a pipe transfer is requested
        @param iq_id: id of the iq request
        @param from_jid: jid of the sender
        @param si_id: Stream Initiation session id
        @param si_mime_type: Mime type of the pipe (or default "application/octet-stream" if unknown)
        @param si_el: domish.Element of the request
        @param profile: %(doc_profile)s"""
        info (_("EXP-PIPE file transfer requested"))
        debug(si_el.toXml())
        client = self.host.getClient(profile)
        if not client:
            raise ProfileNotInCacheError
        pipe_elts = filter(lambda elt: elt.name == 'pipe', si_el.elements())
        feature_elts = self.host.plugins["XEP-0020"].getFeatureElt(si_el)
        
        if not pipe_elts:
            warning(_("No pipe element found"))
            self.host.plugins["XEP-0095"].sendBadRequestError(iq_id, from_jid, profile)
            return
            
        if feature_elts:
            feature_el = feature_elts[0]
            form = data_form.Form.fromElement(feature_el.firstChildElement())
            try:
                stream_method = self.host.plugins["XEP-0020"].negociate(feature_el, 'stream-method',self.managed_stream_m)
            except KeyError:
                warning(_("No stream method found"))
                self.host.plugins["XEP-0095"].sendBadRequestError(iq_id, from_jid, profile)
                return
            if not stream_method:
                warning(_("Can't find a valid stream method"))
                self.host.plugins["XEP-0095"].sendFailedError(iq_id, from_jid, profile)
                return
        else:
            warning(_("No feature element found"))
            self.host.plugins["XEP-0095"].sendBadRequestError(iq_id, from_jid, profile)
            return

        #if we are here, the transfer can start, we just need user's agreement
        data={ "id": iq_id, "from":from_jid }
        client._pipe_waiting_for_approval[si_id] = [data, reactor.callLater(300, self._kill_id, si_id), stream_method, [], profile]

        self.host.askConfirmation(si_id, "PIPE_TRANSFER", data, self.confirmationCB, profile)


    def confirmationCB(self, sid, accepted, frontend_data, profile):
        """Called on confirmation answer
        @param sid: file transfer session id
        @param accepted: True if file transfer is accepted
        @param frontend_data: data sent by frontend"""
        client = self.host.getClient(profile)
        if not client:
            raise ProfileNotInCacheError
        data, timeout, stream_method, failed_methods, profile = client._pipe_waiting_for_approval[sid]
        if accepted:
            if timeout.active():
                timeout.cancel()
            try:
                dest_path = frontend_data['dest_path']
            except KeyError:
                error(_('dest path not found in frontend_data'))
                del(client._pipe_waiting_for_approval[sid])
                return
            if stream_method == self.host.plugins["XEP-0065"].NAMESPACE:
                file_obj = open(dest_path, 'w+')
                self.host.plugins["XEP-0065"].prepareToReceive(jid.JID(data['from']), sid, file_obj, None, self._transferSucceeded, self._transferFailed, profile)
            elif stream_method == self.host.plugins["XEP-0047"].NAMESPACE:
                file_obj = open(dest_path, 'w+')
                self.host.plugins["XEP-0047"].prepareToReceive(jid.JID(data['from']), sid, file_obj, None, self._transferSucceeded, self._transferFailed, profile)
            else:
                error(_("Unknown stream method, this should not happen at this stage, cancelling transfer"))
                del(client._pipe_waiting_for_approval[sid])
                return

            #we can send the iq result
            feature_elt = self.host.plugins["XEP-0020"].chooseOption({'stream-method':stream_method})
            misc_elts = []
            misc_elts.append(domish.Element((PROFILE, "file")))
            self.host.plugins["XEP-0095"].acceptStream(data["id"], data['from'], feature_elt, misc_elts, profile)
        else:
            debug (_("Transfer [%s] refused"), sid)
            self.host.plugins["XEP-0095"].sendRejectedError (data["id"], data['from'], profile=profile)
            del(client._pipe_waiting_for_approval[sid])

    def _transferSucceeded(self, sid, file_obj, stream_method, profile):
        """Called by the stream method when transfer successfuly finished
        @param id: stream id"""
        client = self.host.getClient(profile)
        if not client:
            raise ProfileNotInCacheError
        file_obj.close()
        info(_('Transfer %s successfuly finished') % sid)
        del(client._pipe_waiting_for_approval[sid])

    def _transferFailed(self, sid, file_obj, stream_method, reason, profile):
        """Called when something went wrong with the transfer
        @param id: stream id
        @param reason: can be TIMEOUT, IO_ERROR, PROTOCOL_ERROR"""
        client = self.host.getClient(profile)
        if not client:
            raise ProfileNotInCacheError
        data, timeout, stream_method, failed_methods, profile = client._pipe_waiting_for_approval[sid]
        warning(_('Transfer %(id)s failed with stream method %(s_method)s') % { 'id': sid,
                                                                                 's_method': stream_method })
        filepath = file_obj.name
        file_obj.close()
        #TODO: session remenber (within a time limit) when a stream method fail, and avoid that stream method with full jid for the rest of the session
        warning(_("All stream methods failed, can't transfer the file"))
        del(client._pipe_waiting_for_approval[sid])

    def pipeCb(self, filepath, sid, profile, IQ):
        if IQ['type'] == "error":
            stanza_err = jab_error.exceptionFromStanza(IQ)
            if stanza_err.code == '403' and stanza_err.condition == 'forbidden':
                debug(_("Pipe transfer refused by %s") % IQ['from'])
                self.host.bridge.newAlert(_("The contact %s refused your pipe stream") % IQ['from'], _("Pipe stream refused"), "INFO", profile)
            else:
                warning(_("Error during pipe stream transfer with %s") % IQ['from'])
                self.host.bridge.newAlert(_("Something went wrong during the pipe stream session intialisation with %s") % IQ['from'], _("Pipe stream error"), "ERROR", profile)
            return

        si_elt = IQ.firstChildElement()

        if IQ['type'] != "result" or not si_elt or si_elt.name != "si":
            error(_("Protocol error during file transfer"))
            return

        feature_elts = self.host.plugins["XEP-0020"].getFeatureElt(si_elt)
        if not feature_elts:
            warning(_("No feature element"))
            return
        
        choosed_options = self.host.plugins["XEP-0020"].getChoosedOptions(feature_elts[0])
        try:
            stream_method = choosed_options["stream-method"]
        except KeyError:
            warning(_("No stream method choosed"))
            return

        if stream_method == self.host.plugins["XEP-0065"].NAMESPACE:
           #fd = os.open(filepath, os.O_RDONLY | os.O_NONBLOCK) #XXX: non blocking openingl cause issues with XEP-0065's FileSender
           #file_obj = os.fdopen(fd, 'r')
           file_obj = open(filepath, 'r') #XXX: we have to be sure that filepath is well opened, as reading can block it
           self.host.plugins["XEP-0065"].startStream(file_obj, jid.JID(IQ['from']), sid, None, self.sendSuccessCb, self.sendFailureCb, None, profile)
        elif stream_method == self.host.plugins["XEP-0047"].NAMESPACE:
           #fd = os.open(filepath, os.O_RDONLY | os.O_NONBLOCK) #XXX: non blocking openingl cause issues with XEP-0065's FileSender
           #file_obj = os.fdopen(fd, 'r')
           file_obj = open(filepath, 'r') #XXX: we have to be sure that filepath is well opened, as reading can block it
           self.host.plugins["XEP-0047"].startStream(file_obj, jid.JID(IQ['from']), sid, None, self.sendSuccessCb, self.sendFailureCb, None, profile)
        else:
            warning(_("Invalid stream method received"))

    def pipeOut(self, to_jid, filepath, data={}, profile_key='@DEFAULT@'):
        """send a file using EXP-PIPE
        @to_jid: recipient
        @filepath: absolute path to the named pipe to send
        @data: dictionnary with the optional data
        @param profile_key: %(doc_profile_key)s
        @return: an unique id to identify the transfer
        """
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            warning(_("Trying to send a file from an unknown profile"))
            return ""
        feature_elt = self.host.plugins["XEP-0020"].proposeFeatures({'stream-method': self.managed_stream_m})
       
        pipe_transfer_elts = []
        
        pipe_elt = domish.Element((PROFILE, 'pipe'))
        pipe_transfer_elts.append(pipe_elt)

        sid, offer = self.host.plugins["XEP-0095"].proposeStream(jid.JID(to_jid), PROFILE, feature_elt, pipe_transfer_elts, profile_key = profile)
        offer.addCallback(self.pipeCb, filepath, sid, profile)
        return sid

    def sendSuccessCb(self, sid, file_obj, stream_method, profile):
        info(_('Transfer %s successfuly finished') % sid)
        file_obj.close()

    def sendFailureCb(self, sid, file_obj, stream_method, reason, profile):
        file_obj.close()
        warning(_('Transfer %(id)s failed with stream method %(s_method)s %(profile)s') % { 'id': sid, "s_method": stream_method, "profile": profile })

