#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SàT plugin for managing smtp server
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
import warnings
from twisted.internet import protocol,defer
from twisted.words.protocols.jabber import error as jab_error
from twisted.cred import portal,checkers,credentials
from twisted.cred import error as cred_error
from twisted.mail import smtp
from twisted.python import failure
from email.parser import Parser
from email.utils import parseaddr
from twisted.mail.imap4 import LOGINCredentials, PLAINCredentials
import os,os.path
from twisted.internet import reactor
import sys


from zope.interface import implements


PLUGIN_INFO = {
"name": "SMTP server Plugin",
"import_name": "SMTP",
"type": "Misc",
"protocols": [],
"dependencies": ["Maildir"],
"main": "SMTP_server",
"handler": "no",
"description": _("""Create a SMTP server that you can use to send your "normal" type messages""")
}

class SMTP_server():
    
    params = """
    <params>
    <general>
    <category name="Mail Server">
        <param name="SMTP Port" value="10125" type="string" />
    </category>
    </general>
    </params>
    """

    def __init__(self, host):
        info(_("Plugin SMTP Server initialization"))
        self.host = host
        
        #parameters
        host.memory.importParams(self.params)

        port = int(self.host.memory.getParamA("SMTP Port", "Mail Server"))
        info(_("Launching SMTP server on port %d"), port)
        
        self.server_factory = SmtpServerFactory(self.host)
        reactor.listenTCP(port, self.server_factory)

class SatSmtpMessage:
    implements(smtp.IMessage)

    def __init__(self, host, profile):
        self.host=host
        self.profile=profile
        self.message=[]
    
    def lineReceived(self, line):
        """handle another line"""
        self.message.append(line)

    def eomReceived(self):
        """handle end of message"""
        mail = Parser().parsestr("\n".join(self.message))
        try:
            self.host.sendMessage(parseaddr(mail['to'].decode('utf-8','replace'))[1], mail.get_payload().decode('utf-8','replace'), #TODO: manage other charsets
                                  subject=mail['subject'].decode('utf-8','replace'), mess_type='normal', profile_key=self.profile)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error(_("Can't send message: %s") % exc_value) #The email is invalid or incorreclty parsed
            return defer.fail()
        self.message=None
        return defer.succeed(None)

    def connectionLost(self):
        """handle message truncated"""
        raise smtp.SMTPError

class SatSmtpDelivery:
    implements(smtp.IMessageDelivery)

    def __init__(self, host, profile):
        self.host=host
        self.profile=profile

    def receivedHeader(self, helo, origin, recipients):
        """
        Generate the Received header for a message
        @param helo: The argument to the HELO command and the client's IP
        address.
        @param origin: The address the message is from
        @param recipients: A list of the addresses for which this message
        is bound.
        @return: The full \"Received\" header string.
        """
        return "Received:"

    def validateTo(self, user):
        """
        Validate the address for which the message is destined.
        @param user: The address to validate.
        @return: A Deferred which becomes, or a callable which
        takes no arguments and returns an object implementing IMessage.
        This will be called and the returned object used to deliver the
        message when it arrives.
        """
        return lambda: SatSmtpMessage(self.host, self.profile)

    def validateFrom(self, helo, origin):
        """
        Validate the address from which the message originates.
        @param helo: The argument to the HELO command and the client's IP
        address.
        @param origin: The address the message is from
        @return: origin or a Deferred whose callback will be
        passed origin.
        """
        return origin

class SmtpRealm:
    implements(portal.IRealm)

    def __init__(self,host):
        self.host = host

    def requestAvatar(self, avatarID, mind, *interfaces):
        debug('requestAvatar')
        profile=avatarID.decode('utf-8')
        if smtp.IMessageDelivery not in interfaces:
            raise NotImplementedError
        return smtp.IMessageDelivery, SatSmtpDelivery(self.host,profile), lambda:None

class SatProfileCredentialChecker:
    """
    This credential checker check against SàT's profile and associated jabber's password
    Check if the profile exists, and if the password is OK
    Return the profile as avatarId
    """
    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (credentials.IUsernamePassword,
                            credentials.IUsernameHashedPassword)

    
    def __init__(self, host):
        self.host = host

    def _cbPasswordMatch(self, matched, profile):
        if matched:
            return profile.encode('utf-8')
        else:
            return failure.Failure(cred_error.UnauthorizedLogin())

    def requestAvatarId(self, credentials):
        profiles = self.host.memory.getProfilesList()
        if not credentials.username in profiles:
            return defer.fail(cred_error.UnauthorizedLogin())
        password = self.host.memory.getParamA("Password", "Connection", profile_key=credentials.username)
        return defer.maybeDeferred(
            credentials.checkPassword,
            password).addCallback(
            self._cbPasswordMatch, credentials.username)

class SmtpServerFactory(smtp.SMTPFactory):

    def __init__(self, host):
        self.protocol = smtp.ESMTP
        self.host=host
        _portal = portal.Portal(SmtpRealm(self.host))
        _portal.registerChecker(SatProfileCredentialChecker(self.host))
        smtp.SMTPFactory.__init__(self, _portal)

    def startedConnecting(self, connector):
        debug (_("SMTP server connection started"))
        smtp.SMTPFactory.startedConnecting(self, connector)

    def clientConnectionLost(self, connector, reason):
        debug (_("SMTP server connection lost (reason: %s)"), reason)
        smtp.SMTPFactory.clientConnectionLost(self, connector, reason)
    
    def buildProtocol(self, addr):
        p = smtp.SMTPFactory.buildProtocol(self, addr)
        # add the challengers from imap4, more secure and complicated challengers are available
        p.challengers = {"LOGIN": LOGINCredentials, "PLAIN": PLAINCredentials}
        return p

