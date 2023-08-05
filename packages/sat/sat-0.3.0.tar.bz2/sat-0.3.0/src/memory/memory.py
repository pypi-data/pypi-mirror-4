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

from __future__ import with_statement

import os.path
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError
from xml.dom import minidom
from logging import debug, info, warning, error
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from sat.tools.xml_tools import paramsXml2xmlUI
from sat.core.default_config import default_config
from sat.memory.sqlite import SqliteStorage
from sat.memory.persistent import PersistentDict
from sat.core import exceptions

SAVEFILE_PARAM_XML="/param" #xml parameters template
SAVEFILE_DATABASE="/sat.db"


class Params():
    """This class manage parameters with xml"""
    ### TODO: add desciption in params
    
    #TODO: move Watched in a plugin
    default_xml = u"""
    <params>
    <general>
    </general>
    <individual>
        <category name="Connection" label="%(category_connection)s">
            <param name="JabberID" value="name@example.org/SàT" type="string" />
            <param name="Password" value="" type="password" />
            <param name="Server" value="example.org" type="string" />
            <param name="Port" value="5222" type="string" />
            <param name="NewAccount" value="%(label_NewAccount)s" type="button" callback_id="registerNewAccount"/>
            <param name="autoconnect" label="%(label_autoconnect)s" value="true" type="bool" />
            <param name="autodisconnect" label="%(label_autodisconnect)s" value="false"  type="bool" />
        </category>
        <category name="Misc" label="%(category_misc)s">
            <param name="Watched" value="test@Jabber.goffi.int" type="string" />
        </category>
    </individual>
    </params>
    """ % {'category_connection': _("Connection"),
           'label_NewAccount': _("Register new account"),
           'label_autoconnect': _('Connect on frontend startup'),
           'label_autodisconnect': _('Disconnect on frontend closure'),
           'category_misc': _("Misc")
          }

    def load_default_params(self):
        self.dom = minidom.parseString(Params.default_xml.encode('utf-8'))

    def _mergeParams(self, source_node, dest_node):
        """Look for every node in source_node and recursively copy them to dest if they don't exists"""
        def getNodesMap(children):
            ret = {}
            for child in children:
                if child.nodeType == child.ELEMENT_NODE:
                    ret[(child.tagName, child.getAttribute('name'))] = child
            return ret
        source_map = getNodesMap(source_node.childNodes)
        dest_map = getNodesMap(dest_node.childNodes)
        source_set = set(source_map.keys())
        dest_set = set(dest_map.keys())
        to_add = source_set.difference(dest_set)
        
        for node_key in to_add:
            dest_node.appendChild(source_map[node_key].cloneNode(True))

        to_recurse = source_set - to_add
        for node_key in to_recurse:
            self._mergeParams(source_map[node_key], dest_map[node_key])

    def load_xml(self, xml_file):
        """Load parameters template from file"""
        self.dom = minidom.parse(xml_file)
        default_dom = minidom.parseString(Params.default_xml.encode('utf-8'))
        self._mergeParams(default_dom.documentElement, self.dom.documentElement)
    
    def loadGenParams(self):
        """Load general parameters data from storage
        @return: deferred triggered once params are loaded"""
        return self.storage.loadGenParams(self.params_gen)
        
    def loadIndParams(self, profile, cache=None):
        """Load individual parameters
        set self.params cache or a temporary cache
        @param profile: profile to load (*must exist*)
        @param cache: if not None, will be used to store the value, as a short time cache
        @return: deferred triggered once params are loaded"""
        if cache == None:
            self.params[profile] = {}
        return self.storage.loadIndParams(self.params[profile] if cache==None else cache, profile)
   
    def purgeProfile(self, profile):
        """Remove cache data of a profile
        @param profile: %(doc_profile)s"""
        try:
            del self.params[profile]
        except KeyError:
            error(_("Trying to purge cache of a profile not in memory: [%s]") % profile)

    def save_xml(self, file):
        """Save parameters template to xml file"""
        with open(file, 'wb') as xml_file:
            xml_file.write(self.dom.toxml('utf-8'))

    def __init__(self, host, storage):
        debug("Parameters init")
        self.host = host
        self.storage = storage
        self.default_profile = None
        self.params = {}
        self.params_gen = {}
        host.set_const('savefile_param_xml', SAVEFILE_PARAM_XML)
        host.registerGeneralCB("registerNewAccount", host.registerNewAccountCB)

    def createProfile(self, profile):
        """Create a new profile
        @param profile: profile of the profile"""
        #FIXME: must be asynchronous and call the callback once the profile actually exists
        if self.storage.hasProfile(profile):
            info (_('The profile [%s] already exists') % (profile,))
            return True
        if not self.host.trigger.point("ProfileCreation", profile):
            return False
        self.storage.createProfile(profile)
        return False

    def asyncCreateProfile(self, profile):
        """Create a new profile
        @param profile: name of the profile
        @param callback: called when the profile actually exists in database and memory
        @param errback: called with a string constant as parameter:
                        - CONFLICT: the profile already exists
                        - CANCELED: profile creation canceled
        """
        if self.storage.hasProfile(profile):
            info (_('The profile name already exists'))
            return defer.fail("CONFLICT")
        if not self.host.trigger.point("ProfileCreation", profile):
            return defer.fail("CANCEL")
        return self.storage.createProfile(profile)


    def deleteProfile(self, profile):
        """Delete an existing profile
        @param profile: name of the profile"""
        #TODO: async equivalent, like for createProfile
        if not self.storage.hasProfile(profile):
            error(_('Trying to delete an unknown profile'))
            return True
        if self.host.isConnected(profile):
            error(_("Trying to delete a connected profile"))
            raise exceptions.NotConnectedProfileError
        self.storage.deleteProfile(profile)
        return False

    def getProfileName(self, profile_key):
        """return profile according to profile_key
        @param profile_key: profile name or key which can be
                            @ALL@ for all profiles
                            @DEFAULT@ for default profile
        @return: requested profile name or None if it doesn't exist"""
        if profile_key=='@DEFAULT@':
            default = self.host.memory.memory_data.get('Profile_default')
            if not default:
                info(_('No default profile, returning first one')) #TODO: manage real default profile
                default = self.host.memory.memory_data['Profile_default'] = self.storage.getProfilesList()[0]
            return default #FIXME: temporary, must use real default value, and fallback to first one if it doesn't exists
        if not self.storage.hasProfile(profile_key):
            info (_('Trying to access an unknown profile'))
            return ""
        return profile_key

    def __get_unique_node(self, parent, tag, name):
        """return node with given tag
        @param parent: parent of nodes to check (e.g. documentElement)
        @param tag: tag to check (e.g. "category")
        @param name: name to check (e.g. "JID")
        @return: node if it exist or None
        """
        for node in parent.childNodes:
            if node.nodeName == tag and node.getAttribute("name") == name:
                #the node already exists
                return node
        #the node is new
        return None

    def importParams(self, xml):
        """import xml in parameters, do nothing if the param already exist
        @param xml: parameters in xml form"""
        src_dom = minidom.parseString(xml.encode('utf-8'))

        def import_node(tgt_parent, src_parent):
            for child in src_parent.childNodes:
                if child.nodeName == '#text':
                    continue
                node = self.__get_unique_node(tgt_parent, child.nodeName, child.getAttribute("name"))
                if not node: #The node is new
                    tgt_parent.appendChild(child)
                else:
                    import_node(node, child)

        import_node(self.dom.documentElement, src_dom.documentElement)

    def __default_ok(self, value, name, category):
        #FIXME: gof: will not work with individual parameters
        self.setParam(name, value, category) #FIXME: better to set param xml value ???

    def __default_ko(self, failure, name, category):
        error (_("Can't determine default value for [%(category)s/%(name)s]: %(reason)s") % {'category':category, 'name':name, 'reason':str(failure.value)})

    def setDefault(self, name, category, callback, errback=None):
        """Set default value of parameter
        'default_cb' attibute of parameter must be set to 'yes'
        @param name: name of the parameter
        @param category: category of the parameter
        @param callback: must return a string with the value (use deferred if needed)
        @param errback: must manage the error with args failure, name, category
        """
        #TODO: send signal param update if value changed
        node =  self.__getParamNode(name, category, '@ALL@')
        if not node:
            error(_("Requested param [%(name)s] in category [%(category)s] doesn't exist !") % {'name':name, 'category':category})
            return
        if node[1].getAttribute('default_cb') == 'yes':
            del node[1].attributes['default_cb']
            d = defer.maybeDeferred(callback)
            d.addCallback(self.__default_ok, name, category)
            d.addErrback(errback or self.__default_ko, name, category)

    def __getAttr(self, node, attr, value):
        """ get attribute value
        @param node: XML param node
        @param attr: name of the attribute to get (e.g.: 'value' or 'type')
        @param value: user defined value"""
        if attr == 'value':
            value_to_use = value if value!=None else node.getAttribute(attr) #we use value (user defined) if it exist, else we use node's default value
            if node.getAttribute('type') == 'bool':
                return value_to_use.lower() not in ('false','0')
            return value_to_use
        return node.getAttribute(attr)

    def __type_to_string(self, result):
        """ convert result to string, according to its type """
        if isinstance(result,bool):
            return "true" if result else "false"
        return result

    def getStringParamA(self, name, category, attr="value", profile_key="@DEFAULT@"):
        """ Same as getParamA but for bridge: convert non string value to string """
        return self.__type_to_string(self.getParamA(name, category, attr, profile_key))

    def getParamA(self, name, category, attr="value", profile_key="@DEFAULT@"):
        """Helper method to get a specific attribute
           @param name: name of the parameter
           @param category: category of the parameter
           @param attr: name of the attribute (default: "value")
           @param profile: owner of the param (@ALL@ for everyone)
           
           @return: attribute"""
        #FIXME: looks really dirty and buggy, need to be reviewed/refactored
        node = self.__getParamNode(name, category)
        if not node:
            error(_("Requested param [%(name)s] in category [%(category)s] doesn't exist !") % {'name':name, 'category':category})
            raise exceptions.NotFound

        if node[0] == 'general':
            value = self.__getParam(None, category, name, 'general')
            return self.__getAttr(node[1], attr, value)
        
        assert(node[0] == 'individual')

        profile = self.getProfileName(profile_key)
        if not profile:
            error(_('Requesting a param for an non-existant profile'))
            raise exceptions.ProfileUnknownError
        
        if profile not in self.params:
            error(_('Requesting synchronous param for not connected profile'))
            raise exceptions.NotConnectedProfileError(profile)

        if attr == "value": 
            value = self.__getParam(profile, category, name)
            return self.__getAttr(node[1], attr, value)

    def asyncGetStringParamA(self, name, category, attr="value", profile_key="@DEFAULT@"):
        d = self.asyncGetParamA(name, category, attr, profile_key)
        d.addCallback(self.__type_to_string)
        return d

    def asyncGetParamA(self, name, category, attr="value", profile_key="@DEFAULT@"):
        """Helper method to get a specific attribute
           @param name: name of the parameter
           @param category: category of the parameter
           @param attr: name of the attribute (default: "value")
           @param profile: owner of the param (@ALL@ for everyone)"""
        node = self.__getParamNode(name, category)
        if not node:
            error(_("Requested param [%(name)s] in category [%(category)s] doesn't exist !") % {'name':name, 'category':category})
            return None

        if node[0] == 'general':
            value = self.__getParam(None, category, name, 'general')
            return defer.succeed(self.__getAttr(node[1], attr, value))
        
        assert(node[0] == 'individual')

        profile = self.getProfileName(profile_key)
        if not profile:
            error(_('Requesting a param for a non-existant profile'))
            return defer.fail()
        
        if attr != "value": 
            return defer.succeed(node[1].getAttribute(attr))
        try:
            value = self.__getParam(profile, category, name)
            return defer.succeed(self.__getAttr(node[1], attr, value))
        except exceptions.ProfileNotInCacheError:
            #We have to ask data to the storage manager
            d = self.storage.getIndParam(category, name, profile)
            return d.addCallback(lambda value: self.__getAttr(node[1], attr, value))

    def __getParam(self, profile, category, name, _type='individual', cache=None):
        """Return the param, or None if it doesn't exist
        @param profile: the profile name (not profile key, i.e. name and not something like @DEFAULT@)
        @param category: param category
        @param name: param name
        @param _type: "general" or "individual"
        @param cache: temporary cache, to use when profile is not logged
        @return: param value or None if it doesn't exist
        """
        if _type == 'general':
            if self.params_gen.has_key((category, name)):
                return self.params_gen[(category, name)]
            return None  #This general param has the default value
        assert (_type == 'individual')
        if self.params.has_key(profile):
            cache = self.params[profile] # if profile is in main cache, we use it,
                                         # ignoring the temporary cache
        elif cache == None: #else we use the temporary cache if it exists, or raise an exception
            raise exceptions.ProfileNotInCacheError
        if not cache.has_key((category, name)):
            return None
        return cache[(category, name)]

    def __constructProfileXml(self, profile):
        """Construct xml for asked profile, filling values when needed
        /!\ as noticed in doc, don't forget to unlink the minidom.Document
        @param profile: profile name (not key !)
        @return: a deferred that fire a minidom.Document of the profile xml (cf warning above)
        """
        def constructProfile(ignore,profile_cache):
            prof_xml = minidom.parseString('<params/>')
            cache = {}

            for type_node in self.dom.documentElement.childNodes:
                if type_node.nodeName == 'general' or type_node.nodeName == 'individual':  #we use all params, general and individual
                    for cat_node in type_node.childNodes:
                        if cat_node.nodeName == 'category':
                            category = cat_node.getAttribute('name')
                            if not cache.has_key(category):
                                cache[category] = dest_cat = cat_node.cloneNode(True) #we make a copy for the new xml
                                new_node = True
                            else:
                                dest_cat = cache[category]
                                new_node = False #It's not a new node, we will merge information
                            params = cat_node.getElementsByTagName("param")
                            dest_params = {}
                            for node in dest_cat.childNodes:
                                if node.nodeName != "param":
                                    continue
                                dest_params[node.getAttribute('name')] = node

                            for param_node in params:
                                name = param_node.getAttribute('name')
                                
                                if name not in dest_params:
                                    dest_params[name] = param_node.cloneNode(True)
                                    dest_cat.appendChild(dest_params[name])

                                profile_value = self.__getParam(profile, category, name, type_node.nodeName, cache=profile_cache)
                                if profile_value!=None:  #there is a value for this profile, we must change the default
                                    dest_params[name].setAttribute('value', profile_value)
                            if new_node:
                                prof_xml.documentElement.appendChild(dest_cat)
            return prof_xml
        
        
        if self.params.has_key(profile):
            d = defer.succeed(None)
            profile_cache = self.params[profile]
        else:
            #profile is not in cache, we load values in a short time cache
            profile_cache = {}
            d = self.loadIndParams(profile, profile_cache)

        return d.addCallback(constructProfile, profile_cache)

    def getParamsUI(self, profile_key):
        """Return a SàT XMLUI for parameters, with given profile"""
        profile = self.getProfileName(profile_key)
        if not profile:
            error(_("Asking params for inexistant profile"))
            return ""
        d = self.getParams(profile)
        return d.addCallback(lambda param_xml:paramsXml2xmlUI(param_xml))

    def getParams(self, profile_key):
        """Construct xml for asked profile
        Take params xml as skeleton"""
        profile = self.getProfileName(profile_key)
        if not profile:
            error(_("Asking params for inexistant profile"))
            return ""
        
        def returnXML(prof_xml):
            return_xml = prof_xml.toxml()
            prof_xml.unlink()
            return return_xml

        return self.__constructProfileXml(profile).addCallback(returnXML) 

    def getParamsForCategory(self, category, profile_key):
        """Return node's xml for selected category"""
        #TODO: manage category of general type (without existant profile)
        profile = self.getProfileName(profile_key)
        if not profile:
            error(_("Asking params for inexistant profile"))
            return ""

        def returnCategoryXml(prof_xml):
            for node in prof_xml.getElementsByTagName("category"):
                if node.nodeName == "category" and node.getAttribute("name") == category:
                    result = node.toxml()
                    prof_xml.unlink()
                    return result

            prof_xml.unlink()
            return "<category />"
        
        d = self.__constructProfileXml(profile)
        return d.addCallback(returnCategoryXml)

    def __getParamNode(self, name, category, _type="@ALL@"): #FIXME: is _type useful ?
        """Return a node from the param_xml
        @param name: name of the node
        @param category: category of the node
        @_type: keyword for search:
                                    @ALL@ search everywhere
                                    @GENERAL@ only search in general type
                                    @INDIVIDUAL@ only search in individual type
        @return: a tuple with the node type and the the node, or None if not found"""

        for type_node in self.dom.documentElement.childNodes:
            if ( ((_type == "@ALL@" or _type == "@GENERAL@") and type_node.nodeName == 'general') 
            or ( (_type == "@ALL@" or _type == "@INDIVIDUAL@") and type_node.nodeName == 'individual') ):
                for node in type_node.getElementsByTagName('category'):
                    if node.getAttribute("name") == category:
                        params = node.getElementsByTagName("param")
                        for param in params:
                            if param.getAttribute("name") == name:
                                return (type_node.nodeName, param)
        return None
        
    def getParamsCategories(self):
        """return the categories availables"""
        categories=[]
        for cat in self.dom.getElementsByTagName("category"):
            name = cat.getAttribute("name")
            if name not in categories:
                categories.append(cat.getAttribute("name"))
        return categories

    def setParam(self, name, value, category, profile_key='@NONE@'):
        """Set a parameter, return None if the parameter is not in param xml"""
        #TODO: use different behaviour depending of the data type (e.g. password encrypted)
        if profile_key!="@NONE@":
            profile = self.getProfileName(profile_key)
            if not profile:
                error(_('Trying to set parameter for an unknown profile'))
                return #TODO: throw an error

        node = self.__getParamNode(name, category, '@ALL@')
        if not node:
            error(_('Requesting an unknown parameter (%(category)s/%(name)s)') % {'category':category, 'name':name})
            return
        
        if node[0] == 'general':
            self.params_gen[(category, name)] = value
            self.storage.setGenParam(category, name, value)
            for profile in self.storage.getProfilesList():
                if self.host.isConnected(profile):
                    self.host.bridge.paramUpdate(name, value, category, profile)
            return
        
        assert (node[0] == 'individual')
        assert (profile_key != "@NONE@")
        
        _type = node[1].getAttribute("type")
        if _type=="button":
            print "clique",node.toxml()
        else:
            if self.host.isConnected(profile): #key can not exists if profile is not connected
                self.params[profile][(category, name)] = value
            self.host.bridge.paramUpdate(name, value, category, profile)
            self.storage.setIndParam(category, name, value, profile)

class Memory:
    """This class manage all persistent informations"""

    def __init__(self, host):
        info (_("Memory manager init"))
        self.initialized = defer.Deferred() 
        self.host = host
        self.entitiesCache={} #XXX: keep presence/last resource/other data in cache
                              #     /!\ an entity is not necessarily in roster
        self.subscriptions={}
        self.server_features={} #used to store discovery's informations
        self.server_identities={}
        self.config = self.parseMainConf()
        host.set_const('savefile_database', SAVEFILE_DATABASE)
        database_file = os.path.expanduser(self.getConfig('','local_dir')+
                                        self.host.get_const('savefile_database'))
        self.storage = SqliteStorage(database_file)
        PersistentDict.storage = self.storage
        self.params=Params(host, self.storage)
        self.loadFiles()
        d = self.storage.initialized.addCallback(lambda ignore:self.load())
        self.memory_data = PersistentDict("memory")
        d.addCallback(lambda ignore: self.memory_data.load())
        d.chainDeferred(self.initialized)

    def parseMainConf(self):
        """look for main .ini configuration file, and parse it"""
        _config = SafeConfigParser(defaults=default_config)
        try:
            _config.read(map(os.path.expanduser, ['/etc/sat.conf', '~/sat.conf', '~/.sat.conf', 'sat.conf', '.sat.conf']))
        except:
            error (_("Can't read main config !"))

        return _config

    def getConfig(self, section, name):
        """Get the main configuration option
        @param section: section of the config file (None or '' for DEFAULT)
        @param name: name of the option
        """
        if not section:
            section='DEFAULT'
        try:
            _value = self.config.get(section, name)
        except (NoOptionError, NoSectionError):
            _value = ''

        return os.path.expanduser(_value) if name.endswith('_path') or name.endswith('_dir') else _value


    def loadFiles(self):
        """Load parameters and all memory things from file/db"""
        param_file_xml = os.path.expanduser(self.getConfig('','local_dir')+
                                        self.host.get_const('savefile_param_xml'))

        #parameters template
        if os.path.exists(param_file_xml):
            try:
                self.params.load_xml(param_file_xml)
                debug(_("params template loaded"))
            except Exception as e:
                error (_("Can't load params template: %s") % (e,))
                self.params.load_default_params()
        else:
            info (_("No params template, using default template"))
            self.params.load_default_params()


    def load(self):
        """Load parameters and all memory things from db"""
        #parameters data
        return self.params.loadGenParams()

    def loadIndividualParams(self, profile):
        """Load individual parameters for a profile
        @param profile: %(doc_profile)s"""
        return self.params.loadIndParams(profile)

    def startProfileSession(self, profile):
        """"Iniatialise session for a profile
        @param profile: %(doc_profile)s"""
        info(_("[%s] Profile session started" % profile))
        self.entitiesCache[profile] = {}
    
    def purgeProfileSession(self, profile):
        """Delete cache of data of profile
        @param profile: %(doc_profile)s"""
        info(_("[%s] Profile session purge" % profile))
        self.params.purgeProfile(profile)
        try:
            del self.entitiesCache[profile]
        except KeyError:
            error(_("Trying to purge roster status cache for a profile not in memory: [%s]") % profile)


    def save(self):
        """Save parameters and all memory things to file/db"""
        #TODO: need to encrypt files (at least passwords !) and set permissions
        param_file_xml = os.path.expanduser(self.getConfig('','local_dir')+
                                        self.host.get_const('savefile_param_xml'))
        
        self.params.save_xml(param_file_xml)
        debug(_("params saved"))

    def getProfilesList(self):
        return self.storage.getProfilesList()


    def getProfileName(self, profile_key):
        """Return name of profile from keyword
        @param profile_key: can be the profile name or a keywork (like @DEFAULT@)
        @return: profile name or None if it doesn't exist"""
        return self.params.getProfileName(profile_key)

    def createProfile(self, name):
        """Create a new profile
        @param name: Profile name
        """
        return self.params.createProfile(name)
    
    def asyncCreateProfile(self, name):
        """Create a new profile
        @param name: Profile name
        """
        return self.params.asyncCreateProfile(name)
    
    def deleteProfile(self, name):
        """Delete an existing profile
        @param name: Name of the profile"""
        return self.params.deleteProfile(name)

    def addToHistory(self, from_jid, to_jid, message, _type='chat', timestamp=None, profile="@NONE@"):
        assert(profile!="@NONE@")
        return self.storage.addToHistory(from_jid, to_jid, message, _type, timestamp, profile)

    def getHistory(self, from_jid, to_jid, limit=0, between=True, profile="@NONE@"):
        assert(profile != "@NONE@")
        return self.storage.getHistory(jid.JID(from_jid), jid.JID(to_jid), limit, between, profile)

    def addServerFeature(self, feature, profile):
        """Add a feature discovered from server
        @param feature: string of the feature
        @param profile: which profile is using this server ?"""
        if not self.server_features.has_key(profile):
            self.server_features[profile] = []
        self.server_features[profile].append(feature)
    
    def addServerIdentity(self, category, _type, entity, profile):
        """Add an identity discovered from server
        @param feature: string of the feature
        @param profile: which profile is using this server ?"""
        if not profile in self.server_identities:
            self.server_identities[profile] = {}
        if not self.server_identities[profile].has_key((category, _type)):
            self.server_identities[profile][(category, _type)]=set()
        self.server_identities[profile][(category, _type)].add(entity)

    def getServerServiceEntities(self, category, _type, profile):
        """Return all available entities for a service"""
        if profile in self.server_identities:
            return self.server_identities[profile].get((category, _type), set())
        else:
            return None

    def getServerServiceEntity(self, category, _type, profile):
        """Helper method to get first available entity for a service"""
        entities = self.getServerServiceEntities(category, _type, profile)
        if entities == None:
            warning(_("Entities (%(category)s/%(type)s) not available, maybe they haven't been asked to server yet ?") % {"category":category,
                                                                                                                          "type":_type})
            return None
        else:
            return list(entities)[0] if entities else None

    def hasServerFeature(self, feature, profile_key):
        """Tell if the server of the profile has the required feature"""
        profile = self.getProfileName(profile_key)
        if not profile:
            error (_('Trying find server feature for a non-existant profile'))
            return
        assert(self.server_features.has_key(profile))
        return feature in self.server_features[profile]

    def getLastResource(self, contact, profile_key):
        """Return the last resource used by a contact
        @param contact: contact jid (unicode)
        @param profile_key: %(doc_profile_key)s"""
        profile = self.getProfileName(profile_key)
        if not profile or not self.host.isConnected(profile):
            error(_('Asking contacts for a non-existant or not connected profile'))
            return ""
        entity = jid.JID(contact).userhost()
        if not entity in self.entitiesCache[profile]:
            info(_("Entity not in cache"))
            return ""
        try:
            return self.entitiesCache[profile][entity]["last_resource"]
        except KeyError:
            return ""
    
    def getPresenceStatus(self, profile_key):
        profile = self.getProfileName(profile_key)
        if not profile:
            error(_('Asking contacts for a non-existant profile'))
            return {}
        entities_presence = {}
        for entity in self.entitiesCache[profile]:
            if "presence" in self.entitiesCache[profile][entity]:
                entities_presence[entity] = self.entitiesCache[profile][entity]["presence"]

        debug ("Memory getPresenceStatus (%s)", entities_presence)
        return entities_presence

    def setPresenceStatus(self, entity_jid, show, priority, statuses, profile_key):
        """Change the presence status of an entity"""
        profile = self.getProfileName(profile_key)
        if not profile:
            error(_('Trying to add presence status to a non-existant profile'))
            return
        entity_data = self.entitiesCache[profile].setdefault(entity_jid.userhost(),{})
        resource = jid.parse(entity_jid.full())[2] or ''
        if resource:
            entity_data["last_resource"] = resource
        if not "last_resource" in entity_data:
            entity_data["last_resource"] = ''

        entity_data.setdefault("presence",{})[resource] = (show, priority, statuses)

    def updateEntityData(self, entity_jid, key, value, profile_key):
        """Set a misc data for an entity
        @param entity_jid: JID of the entity
        @param key: key to set (eg: "type")
        @param value: value for this key (eg: "chatroom")
        @param profile_key: %(doc_profile_key)s
        """
        profile = self.getProfileName(profile_key)
        if not profile:
            raise exceptions.UnknownProfileError(_('Trying to get entity data for a non-existant profile'))
        if not profile in self.entitiesCache:
            raise exceptions.ProfileNotInCacheError
        entity_data = self.entitiesCache[profile].setdefault(entity_jid.userhost(),{})
        entity_data[key] = value
        if isinstance(value,basestring):
            self.host.bridge.entityDataUpdated(entity_jid.userhost(), key, value, profile)

    def getEntityData(self, entity_jid, keys_list, profile_key):
        """Get a list of cached values for entity
        @param entity_jid: JID of the entity
        @param keys_list: list of keys to get, empty list for everything
        @param profile_key: %(doc_profile_key)s
        @return: dict withs values for each key in keys_list.
                 if there is no value of a given key, resulting dict will
                 have nothing with that key nether
        @raise: exceptions.UnknownEntityError if entity is not in cache
                exceptions.ProfileNotInCacheError if profile is not in cache 
        """
        profile = self.getProfileName(profile_key)
        if not profile:
            raise exceptions.UnknownProfileError(_('Trying to get entity data for a non-existant profile'))
        if not profile in self.entitiesCache:
            raise exceptions.ProfileNotInCacheError
        if not entity_jid.userhost() in self.entitiesCache[profile]:
            raise exceptions.UnknownEntityError
        entity_data = self.entitiesCache[profile][entity_jid.userhost()]
        if not keys_list:
            return entity_data
        ret = {}
        for key in keys_list:
            if key in entity_data:
                ret[key] = entity_data[key]
        return ret

    def delEntityCache(self, entity_jid, profile_key):
        """Remove cached data for entity
        @param entity_jid: JID of the entity
        """
        profile = self.getProfileName(profile_key)
        try:
            del self.entitiesCache[profile][entity_jid.userhost()]
        except KeyError:
            pass



    def addWaitingSub(self, _type, entity_jid, profile_key):
        """Called when a subcription request is received"""
        profile = self.getProfileName(profile_key)
        assert(profile)
        if not self.subscriptions.has_key(profile):
            self.subscriptions[profile] = {}
        self.subscriptions[profile][entity_jid] = _type
    
    def delWaitingSub(self, entity_jid, profile_key):
        """Called when a subcription request is finished"""
        profile = self.getProfileName(profile_key)
        assert(profile)
        if self.subscriptions.has_key(profile) and self.subscriptions[profile].has_key(entity_jid):
            del self.subscriptions[profile][entity_jid]
    
    def getWaitingSub(self, profile_key):
        """Called to get a list of currently waiting subscription requests"""
        profile = self.getProfileName(profile_key)
        if not profile:
            error(_('Asking waiting subscriptions for a non-existant profile'))
            return {}
        if not self.subscriptions.has_key(profile):
            return {}
        
        return self.subscriptions[profile]

    def getStringParamA(self, name, category, attr="value", profile_key='@DEFAULT@'):
        return self.params.getStringParamA(name, category, attr, profile_key)
    
    def getParamA(self, name, category, attr="value", profile_key='@DEFAULT@'):
        return self.params.getParamA(name, category, attr, profile_key)
    
    def asyncGetParamA(self, name, category, attr="value", profile_key='@DEFAULT@'):
        return self.params.asyncGetParamA(name, category, attr, profile_key)
    
    def asyncGetStringParamA(self, name, category, attr="value", profile_key='@DEFAULT@'):
        return self.params.asyncGetStringParamA(name, category, attr, profile_key)
    
    def getParamsUI(self, profile_key):
        return self.params.getParamsUI(profile_key)
  
    def getParams(self, profile_key):
        return self.params.getParams(profile_key) 
    
    def getParamsForCategory(self, category, profile_key):
        return self.params.getParamsForCategory(category, profile_key) 
    
    def getParamsCategories(self):
        return self.params.getParamsCategories()
    
    def setParam(self, name, value, category, profile_key):
        return self.params.setParam(name, value, category, profile_key)

    def importParams(self, xml):
        return self.params.importParams(xml)
    
    def setDefault(self, name, category, callback, errback=None):
        return self.params.setDefault(name, category, callback, errback)
