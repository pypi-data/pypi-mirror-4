#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SAT plugin for microbloging with roster access
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
from twisted.internet import defer
from twisted.words.protocols.jabber import jid

from wokkel import disco, data_form, iwokkel

from zope.interface import implements

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

NS_PUBSUB = 'http://jabber.org/protocol/pubsub'
NS_GROUPBLOG = 'http://goffi.org/protocol/groupblog'
NS_NODE_PREFIX = 'urn:xmpp:groupblog:'
#NS_PUBSUB_EXP = 'http://goffi.org/protocol/pubsub' #for non official features
NS_PUBSUB_EXP = NS_PUBSUB #XXX: we can't use custom namespace as Wokkel's PubSubService use official NS
NS_PUBSUB_ITEM_ACCESS = NS_PUBSUB_EXP + "#item-access"
NS_PUBSUB_CREATOR_JID_CHECK = NS_PUBSUB_EXP + "#creator-jid-check"
NS_PUBSUB_ITEM_CONFIG = NS_PUBSUB_EXP + "#item-config"
NS_PUBSUB_AUTO_CREATE = NS_PUBSUB + "#auto-create"
OPT_ROSTER_GROUPS_ALLOWED = 'pubsub#roster_groups_allowed'
OPT_ACCESS_MODEL = 'pubsub#access_model'
OPT_PERSIST_ITEMS = 'pubsub#persist_items'
OPT_MAX_ITEMS = 'pubsub#max_items'
OPT_NODE_TYPE = 'pubsub#node_type'
OPT_SUBSCRIPTION_TYPE = 'pubsub#subscription_type'
OPT_SUBSCRIPTION_DEPTH = 'pubsub#subscription_depth'
TYPE_COLLECTION = 'collection'

PLUGIN_INFO = {
"name": "Group blogging throught collections",
"import_name": "groupblog",
"type": "MISC",
"protocols": [],
"dependencies": ["XEP-0277"],
"main": "GroupBlog",
"handler": "yes",
"description": _("""Implementation of microblogging with roster access""")
}

class NoCompatiblePubSubServerFound(Exception):
    pass

class BadAccessTypeError(Exception):
    pass

class BadAccessListError(Exception):
    pass

class UnknownType(Exception):
    pass

class GroupBlog():
    """This class use a SàT PubSub Service to manage access on microblog"""

    def __init__(self, host):
        info(_("Group blog plugin initialization"))
        self.host = host

        host.bridge.addMethod("sendGroupBlog", ".plugin", in_sign='sasss', out_sign='',
                               method=self.sendGroupBlog)
       
        host.bridge.addMethod("getLastGroupBlogs", ".plugin",
                              in_sign='sis', out_sign='aa{ss}',
                              method=self.getLastGroupBlogs,
                              async = True)

        host.bridge.addMethod("getMassiveLastGroupBlogs", ".plugin",
                              in_sign='sasis', out_sign='a{saa{ss}}',
                              method=self.getMassiveLastGroupBlogs,
                              async = True)
        
        host.bridge.addMethod("subscribeGroupBlog", ".plugin", in_sign='ss', out_sign='',
                               method=self.subscribeGroupBlog,
                               async = True)
       
        host.bridge.addMethod("massiveSubscribeGroupBlogs", ".plugin", in_sign='sass', out_sign='',
                               method=self.massiveSubscribeGroupBlogs,
                               async = True)
        
        host.trigger.add("PubSubItemsReceived", self.pubSubItemsReceivedTrigger)
       
    
    def getHandler(self, profile):
        return GroupBlog_handler()
       
    @defer.inlineCallbacks
    def initialise(self, profile_key):
        """Check that this data for this profile are initialised, and do it else
        @param client: client of the profile
        @profile_key: %(doc_profile)s"""
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            error(_("Unknown profile"))
            raise Exception("Unknown profile") 
        
        client = self.host.getClient(profile)
        if not client:
            error(_('No client for this profile key: %s') % profile_key)
            raise Exception("Unknown profile") 
        yield client.client_initialized #we want to be sure that the client is initialized
        
        #we first check that we have a item-access pubsub server
        if not hasattr(client,"item_access_pubsub"):
            debug(_('Looking for item-access power pubsub server'))
            #we don't have any pubsub server featuring item access yet
            client.item_access_pubsub = None
            client._item_access_pubsub_pending = defer.Deferred()
            for entity in self.host.memory.getServerServiceEntities("pubsub", "service", profile):
                _disco = yield client.disco.requestInfo(entity)
                #if set([NS_PUBSUB_ITEM_ACCESS, NS_PUBSUB_AUTO_CREATE, NS_PUBSUB_CREATOR_JID_CHECK]).issubset(_disco.features):
                if set([NS_PUBSUB_AUTO_CREATE, NS_PUBSUB_CREATOR_JID_CHECK]).issubset(_disco.features):
                    info(_("item-access powered pubsub service found: [%s]") % entity.full())
                    client.item_access_pubsub = entity
            client._item_access_pubsub_pending.callback(None)
        
        if hasattr(client,"_item_access_pubsub_pending"):
            #XXX: we need to wait for item access pubsub service check
            yield client._item_access_pubsub_pending
            del client._item_access_pubsub_pending

        if not client.item_access_pubsub:
            error(_("No item-access powered pubsub server found, can't use group blog"))
            raise NoCompatiblePubSubServerFound

        defer.returnValue((profile, client))

    def pubSubItemsReceivedTrigger(self, event, profile):
        """"Trigger which catch groupblogs events"""
        if event.nodeIdentifier.startswith(NS_NODE_PREFIX):
            publisher = jid.JID(event.nodeIdentifier[len(NS_NODE_PREFIX):])
            origin_host = publisher.host.split('.')
            event_host = event.sender.host.split('.')
            #FIXME: basic origin check, must be improved
            #TODO: automatic security test
            if (not (origin_host)
                or len(event_host) < len(origin_host)
                or event_host[-len(origin_host):] != origin_host):
                warning("Host incoherence between %s and %s (hack attempt ?)" % (unicode(event.sender),
                                                                                 unicode(publisher)))
                return
            for item in event.items:
                microblog_data = self.item2gbdata(item)

                self.host.bridge.personalEvent(publisher.full(), "MICROBLOG", microblog_data, profile)
            return False
        return True


    def _parseAccessData(self, microblog_data, item):
        form_elts = filter(lambda elt: elt.name == "x", item.children)
        for form_elt in form_elts:
            form = data_form.Form.fromElement(form_elt)
            
            if (form.formNamespace == NS_PUBSUB_ITEM_CONFIG):
                access_model = form.get(OPT_ACCESS_MODEL, 'open')
                if access_model == "roster":
                    try:
                        microblog_data["groups"] = '\n'.join(form.fields[OPT_ROSTER_GROUPS_ALLOWED].values)
                    except KeyError:
                        warning("No group found for roster access-model")
                        microblog_data["groups"] = ''
                
                break

    def item2gbdata(self, item):
        """ Convert item to microblog data dictionary + add access data """
        microblog_data = self.host.plugins["XEP-0277"].item2mbdata(item)
        self._parseAccessData(microblog_data, item)
        return microblog_data


    def getNodeName(self, publisher):
        """Retrieve the name of publisher's node
        @param publisher: publisher's jid
        @return: node's name (string)"""
        return NS_NODE_PREFIX + publisher.userhost()



    def _publishMblog(self, service, client, access_type, access_list, message):
        """Actually publish the message on the group blog
        @param service: jid of the item-access pubsub service
        @param client: SatXMPPClient of the published
        @param access_type: one of "PUBLIC", "GROUP", "JID"
        @param access_list: set of entities (empty list for all, groups or jids) allowed to see the item
        @param message: message to publish
        """
        mblog_item = self.host.plugins["XEP-0277"].data2entry({'content':message}, client.profile)
        form = data_form.Form('submit', formNamespace=NS_PUBSUB_ITEM_CONFIG)
        if access_type == "PUBLIC":
            if access_list:
                raise BadAccessListError("access_list must be empty for PUBLIC access")
            access = data_form.Field(None, OPT_ACCESS_MODEL, value="open")
            form.addField(access)
        elif access_type == "GROUP":
            access = data_form.Field(None, OPT_ACCESS_MODEL, value="roster")
            allowed = data_form.Field(None, OPT_ROSTER_GROUPS_ALLOWED, values=access_list)
            form.addField(access)
            form.addField(allowed)
            mblog_item.addChild(form.toElement())
        elif access_type == "JID":
            raise NotImplementedError
        else:
            error(_("Unknown access_type"))
            raise BadAccessTypeError
        defer_blog = self.host.plugins["XEP-0060"].publish(service, self.getNodeName(client.jid), items=[mblog_item], profile_key=client.profile)
        defer_blog.addErrback(self._mblogPublicationFailed)

    def _mblogPublicationFailed(self, failure):
        #TODO
        return failure

    def sendGroupBlog(self, access_type, access_list, message, profile_key='@DEFAULT@'):
        """Publish a microblog with given item access
        @param access_type: one of "PUBLIC", "GROUP", "JID"
        @param access_list: list of authorized entity (empty list for PUBLIC ACCESS,
                            list of groups or list of jids) for this item
        @param message: microblog
        @profile_key: %(doc_profile)s
        """
        print "sendGroupBlog"
        def initialised(result):
            profile, client = result
            if access_type == "PUBLIC":
                if access_list:
                    raise Exception("Publishers list must be empty when getting microblogs for all contacts")
                self._publishMblog(client.item_access_pubsub, client, "PUBLIC", [], message)
            elif access_type == "GROUP":
                _groups = set(access_list).intersection(client.roster.getGroups()) #We only keep group which actually exist
                if not _groups:
                    raise BadAccessListError("No valid group")
                self._publishMblog(client.item_access_pubsub, client, "GROUP", _groups, message)
            elif access_type == "JID":
                raise NotImplementedError
            else:
                error(_("Unknown access type"))
                raise BadAccessTypeError 
            
        self.initialise(profile_key).addCallback(initialised)


        
    def getLastGroupBlogs(self, pub_jid, max_items=10, profile_key='@DEFAULT@'):
        """Get the last published microblogs
        @param pub_jid: jid of the publisher
        @param max_items: how many microblogs we want to get (see XEP-0060 #6.5.7)
        @param profile_key: profile key
        @return: list of microblog data (dict)
        """
        
        def initialised(result):
            profile, client = result
            d = self.host.plugins["XEP-0060"].getItems(client.item_access_pubsub, self.getNodeName(jid.JID(pub_jid)),
                                                       max_items=max_items, profile_key=profile_key)
            d.addCallback(lambda items: map(self.item2gbdata, items))
            d.addErrback(lambda ignore: {}) #TODO: more complete error management (log !)
            return d

        #TODO: we need to use the server corresponding the the host of the jid
        return self.initialise(profile_key).addCallback(initialised)

    def getMassiveLastGroupBlogs(self, publishers_type, publishers, max_items=10, profile_key='@DEFAULT@'):
        """Get the last published microblogs for a list of groups or jids
        @param publishers_type: type of the list of publishers (one of "GROUP" or "JID" or "ALL")
        @param publishers: list of publishers, according to "publishers_type" (list of groups or list of jids)
        @param max_items: how many microblogs we want to get
        @param profile_key: profile key
        """
        def sendResult(result):
            """send result of DeferredList (list of microblogs to the calling method"""
            
            ret = {}

            for (success, value) in result:
                if success:
                    source_jid, data = value
                    ret[source_jid] = data
            
            return ret

        def initialised(result):
            profile, client = result

            if publishers_type == "ALL":
                contacts = client.roster.getItems()
                jids = [contact.jid.userhost() for contact in contacts]
            elif publishers_type == "GROUP":
                jids = []
                for _group in publishers:
                    jids.extend(client.roster.getJidsFromGroup(_group))
            elif publishers_type == 'JID':
                jids = publishers
            else:
                raise UnknownType
            
            mblogs = []
            
            for _jid in jids:
                d = self.host.plugins["XEP-0060"].getItems(client.item_access_pubsub, self.getNodeName(jid.JID(_jid)),
                                                           max_items=max_items, profile_key=profile_key)
                d.addCallback(lambda items, source_jid: (source_jid, map(self.item2gbdata, items)), _jid)
                mblogs.append(d)
            dlist = defer.DeferredList(mblogs)
            dlist.addCallback(sendResult)
            
            return dlist


        #TODO: custom exception
        if publishers_type not in ["GROUP", "JID", "ALL"]:
            raise Exception("Bad call, unknown publishers_type")
        if publishers_type=="ALL" and publishers:
            raise Exception("Publishers list must be empty when getting microblogs for all contacts")
        return self.initialise(profile_key).addCallback(initialised)
        #TODO: we need to use the server corresponding the the host of the jid

    def subscribeGroupBlog(self, pub_jid, profile_key='@DEFAULT'):
        def initialised(result):
            profile, client = result
            d = self.host.plugins["XEP-0060"].subscribe(client.item_access_pubsub, self.getNodeName(jid.JID(pub_jid)),
                                                        profile_key=profile_key)
            return d

        #TODO: we need to use the server corresponding the the host of the jid
        return self.initialise(profile_key).addCallback(initialised)


    def massiveSubscribeGroupBlogs(self, publishers_type, publishers, profile_key='@DEFAULT@'):
        """Subscribe microblogs for a list of groups or jids
        @param publishers_type: type of the list of publishers (one of "GROUP" or "JID" or "ALL")
        @param publishers: list of publishers, according to "publishers_type" (list of groups or list of jids)
        @param profile_key: profile key
        """
        def initialised(result):
            profile, client = result

            if publishers_type == "ALL":
                contacts = client.roster.getItems()
                jids = [contact.jid.userhost() for contact in contacts]
            elif publishers_type == "GROUP":
                jids = []
                for _group in publishers:
                    jids.extend(client.roster.getJidsFromGroup(_group))
            elif publishers_type == 'JID':
                jids = publishers
            else:
                raise UnknownType

            mblogs = []
            for _jid in jids:
                d = self.host.plugins["XEP-0060"].subscribe(client.item_access_pubsub, self.getNodeName(jid.JID(_jid)),
                                                            profile_key=profile_key)
                mblogs.append(d)
            dlist = defer.DeferredList(mblogs)
            return dlist


        #TODO: custom exception
        if publishers_type not in ["GROUP", "JID", "ALL"]:
            raise Exception("Bad call, unknown publishers_type")
        if publishers_type=="ALL" and publishers:
            raise Exception("Publishers list must be empty when getting microblogs for all contacts")
        return self.initialise(profile_key).addCallback(initialised)
        #TODO: we need to use the server corresponding the the host of the jid



class GroupBlog_handler(XMPPHandler):
    implements(iwokkel.IDisco)
    
    def getDiscoInfo(self, requestor, target, nodeIdentifier=''):
        return [disco.DiscoFeature(NS_GROUPBLOG)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=''):
        return []

