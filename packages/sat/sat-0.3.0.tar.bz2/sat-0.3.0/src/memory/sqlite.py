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


from logging import debug, info, warning, error
from twisted.enterprise import adbapi
from twisted.internet import defer
import os.path
import time
import cPickle as pickle

class SqliteStorage():
    """This class manage storage with Sqlite database"""


    def __init__(self, db_filename):
        """Connect to the given database
        @param db_filename: full path to the Sqlite database"""
        self.initialized = defer.Deferred() #triggered when memory is fully initialised and ready
        init_defers = [] #list of deferred we have to wait to before initialisation is complete
        self.profiles={} #we keep cache for the profiles (key: profile name, value: profile id)

        info(_("Connecting database"))
        new_base = not os.path.exists(db_filename) #do we have to create the database ?
        self.dbpool = adbapi.ConnectionPool("sqlite3", db_filename, check_same_thread=False)
        init_defers.append(self.dbpool.runOperation("PRAGMA foreign_keys = ON").addErrback(lambda x: error(_("Can't activate foreign keys"))))
        if new_base:
            info(_("The database is new, creating the tables"))
            database_creation = [
            "CREATE TABLE profiles (id INTEGER PRIMARY KEY ASC, name TEXT, UNIQUE (name))",
            "CREATE TABLE message_types (type TEXT PRIMARY KEY)",
            "INSERT INTO message_types VALUES ('chat')",
            "INSERT INTO message_types VALUES ('error')",
            "INSERT INTO message_types VALUES ('groupchat')",
            "INSERT INTO message_types VALUES ('headline')",
            "INSERT INTO message_types VALUES ('normal')",
            "CREATE TABLE history (id INTEGER PRIMARY KEY ASC, profile_id INTEGER, source TEXT, dest TEXT, source_res TEXT, dest_res TEXT, timestamp DATETIME, message TEXT, type TEXT, FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE, FOREIGN KEY(type) REFERENCES message_types(type))",
            "CREATE TABLE param_gen (category TEXT, name TEXT, value TEXT, PRIMARY KEY (category,name))",
            "CREATE TABLE param_ind (category TEXT, name TEXT, profile_id INTEGER, value TEXT, PRIMARY KEY (category,name,profile_id), FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE)",
            "CREATE TABLE private_gen (namespace TEXT, key TEXT, value TEXT, PRIMARY KEY (namespace, key))",
            "CREATE TABLE private_ind (namespace TEXT, key TEXT, profile_id INTEGER, value TEXT, PRIMARY KEY (namespace, key, profile_id), FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE)",
            "CREATE TABLE private_gen_bin (namespace TEXT, key TEXT, value BLOB, PRIMARY KEY (namespace, key))",
            "CREATE TABLE private_ind_bin (namespace TEXT, key TEXT, profile_id INTEGER, value BLOB, PRIMARY KEY (namespace, key, profile_id), FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE)",
            ]
            for op in database_creation:
                d = self.dbpool.runOperation(op)
                d.addErrback(lambda x: error(_("Error while creating tables in database [QUERY: %s]") % op ))
                init_defers.append(d)

        def fillProfileCache(ignore):
            d = self.dbpool.runQuery("SELECT name,id FROM profiles").addCallback(self._profilesCache)
            d.chainDeferred(self.initialized)
            
        defer.DeferredList(init_defers).addCallback(fillProfileCache)

    #Profiles
    def _profilesCache(self, profiles_result):
        """Fill the profiles cache
        @param profiles_result: result of the sql profiles query"""
        for profile in profiles_result:
            name, id = profile
            self.profiles[name] = id 
   
    def getProfilesList(self):
        """"Return list of all registered profiles"""
        return self.profiles.keys()

    def hasProfile(self, profile_name):
        """return True if profile_name exists
        @param profile_name: name of the profile to check"""
        return self.profiles.has_key(profile_name)
    
    def createProfile(self, name):
        """Create a new profile
        @param name: name of the profile
        @return: deferred triggered once profile is actually created"""
        def getProfileId(ignore):
            return self.dbpool.runQuery("SELECT (id) FROM profiles WHERE name = ?", (name,))
       
        def profile_created(profile_id):
            _id = profile_id[0][0]
            self.profiles[name] = _id #we synchronise the cache
        
        d = self.dbpool.runQuery("INSERT INTO profiles(name) VALUES (?)", (name,))
        d.addCallback(getProfileId)
        d.addCallback(profile_created)
        return d
    
    def deleteProfile(self, name):
        """Delete profile
        @param name: name of the profile
        @return: deferred triggered once profile is actually deleted"""
        def deletionError(failure):
            error(_("Can't delete profile [%s]") % name)
            return failure
        del self.profiles[name]
        d = self.dbpool.runQuery("DELETE FROM profiles WHERE name = ?", (name,))
        d.addCallback(lambda ignore: info(_("Profile [%s] deleted") % name))
        return d


    #Params
    def loadGenParams(self, params_gen):
        """Load general parameters
        @param params_gen: dictionary to fill
        @return: deferred"""
        def fillParams(result):
            for param in result:
                category,name,value = param
                params_gen[(category, name)] = value
        debug(_("loading general parameters from database")) 
        return self.dbpool.runQuery("SELECT category,name,value FROM param_gen").addCallback(fillParams)

    def loadIndParams(self, params_ind, profile):
        """Load individual parameters
        @param params_ind: dictionary to fill
        @param profile: a profile which *must* exist
        @return: deferred"""
        def fillParams(result):
            for param in result:
                category,name,value = param
                params_ind[(category, name)] = value
        debug(_("loading individual parameters from database")) 
        d = self.dbpool.runQuery("SELECT category,name,value FROM param_ind WHERE profile_id=?", (self.profiles[profile],))
        d.addCallback(fillParams)
        return d

    def getIndParam(self, category, name, profile):
        """Ask database for the value of one specific individual parameter
        @param category: category of the parameter
        @param name: name of the parameter
        @param profile: %(doc_profile)s
        @return: deferred"""
        d = self.dbpool.runQuery("SELECT value FROM param_ind WHERE category=? AND name=? AND profile_id=?", (category,name,self.profiles[profile]))
        d.addCallback(self.__getFirstResult)
        return d

    def setGenParam(self, category, name, value):
        """Save the general parameters in database
        @param category: category of the parameter
        @param name: name of the parameter
        @param value: value to set
        @return: deferred"""
        d = self.dbpool.runQuery("REPLACE INTO param_gen(category,name,value) VALUES (?,?,?)", (category, name, value))
        d.addErrback(lambda ignore: error(_("Can't set general parameter (%(category)s/%(name)s) in database" % {"category":category, "name":name})))
        return d

    def setIndParam(self, category, name, value, profile):
        """Save the individual parameters in database
        @param category: category of the parameter
        @param name: name of the parameter
        @param value: value to set
        @param profile: a profile which *must* exist
        @return: deferred"""
        d = self.dbpool.runQuery("REPLACE INTO param_ind(category,name,profile_id,value) VALUES (?,?,?,?)", (category, name, self.profiles[profile], value))
        d.addErrback(lambda ignore: error(_("Can't set individual parameter (%(category)s/%(name)s) for [%(profile)s] in database" % {"category":category, "name":name, "profile":profile})))
        return d

    #History
    def addToHistory(self, from_jid, to_jid, message, _type='chat', timestamp=None, profile=None):
        """Store a new message in history
        @param from_jid: full source JID
        @param to_jid: full dest JID
        @param message: message
        @param _type: message type (see RFC 6121 §5.2.2)
        @param timestamp: timestamp in seconds since epoch, or None to use current time
        """
        assert(profile)
        d = self.dbpool.runQuery("INSERT INTO history(source, source_res, dest, dest_res, timestamp, message, type, profile_id) VALUES (?,?,?,?,?,?,?,?)",
                                (from_jid.userhost(), from_jid.resource, to_jid.userhost(), to_jid.resource, timestamp or time.time(),
                                message, _type, self.profiles[profile]))
        d.addErrback(lambda ignore: error(_("Can't save following message in history: from [%(from_jid)s] to [%(to_jid)s] ==> [%(message)s]" %
                                         {"from_jid":from_jid.full(), "to_jid":to_jid.full(), "message":message})))
        return d

    def getHistory(self, from_jid, to_jid, limit=0, between=True, profile=None):
        """Store a new message in history
        @param from_jid: source JID (full, or bare for catchall
        @param to_jid: dest JID (full, or bare for catchall
        @param size: maximum number of messages to get, or 0 for unlimited
        """
        assert(profile)
        def sqliteToDict(query_result):
            query_result.reverse()
            result = []
            for row in query_result:
                timestamp, source, source_res, dest, dest_res, message, _type= row
                result.append((timestamp, "%s/%s" % (source, source_res) if source_res else source,
                                          "%s/%s" % (dest, dest_res) if dest_res else dest,
                                          message, _type))
            return result


        query_parts = ["SELECT timestamp, source, source_res, dest, dest_res, message, type FROM history WHERE profile_id=? AND"]
        values = [self.profiles[profile]]

        def test_jid(_type,_jid):
            values.append(_jid.userhost())
            if _jid.resource:
                values.append(_jid.resource)
                return '(%s=? AND %s_res=?)' % (_type, _type)
            return '%s=?' % (_type,)
        
        if between:
            query_parts.append("(%s OR %s) AND (%s or %s)" % (test_jid('source', from_jid),
                                                               test_jid('source', to_jid),
                                                               test_jid('dest', to_jid),
                                                               test_jid('dest', from_jid)))
        else:
            query_parts.append("%s AND %s") % (test_jid('source', from_jid),
                                               test_jid('dest', to_jid))

        query_parts.append("ORDER BY timestamp DESC")

        if limit:
            query_parts.append("LIMIT ?")
            values.append(limit)
        
        d = self.dbpool.runQuery(" ".join(query_parts), values)
        return d.addCallback(sqliteToDict)

    #Private values
    def loadGenPrivates(self, private_gen, namespace):
        """Load general private values
        @param private_gen: dictionary to fill
        @param namespace: namespace of the values
        @return: deferred"""
        def fillPrivates(result):
            for private in result:
                key,value = private
                private_gen[key] = value
        debug(_("loading general private values [namespace: %s] from database") % (namespace,)) 
        d = self.dbpool.runQuery("SELECT key,value FROM private_gen WHERE namespace=?", (namespace,)).addCallback(fillPrivates)
        return d.addErrback(lambda x: debug(_("No data present in database for namespace %s") % namespace))

    def loadIndPrivates(self, private_ind, namespace, profile):
        """Load individual private values
        @param privates_ind: dictionary to fill
        @param namespace: namespace of the values
        @param profile: a profile which *must* exist
        @return: deferred"""
        def fillPrivates(result):
            for private in result:
                key,value = private
                private_ind[key] = value
        debug(_("loading individual private values [namespace: %s] from database") % (namespace,))
        d = self.dbpool.runQuery("SELECT key,value FROM private_ind WHERE namespace=? AND profile_id=?", (namespace, self.profiles[profile]))
        d.addCallback(fillPrivates)
        return d.addErrback(lambda x: debug(_("No data present in database for namespace %s") % namespace))

    def setGenPrivate(self, namespace, key, value):
        """Save the general private value in database
        @param category: category of the privateeter
        @param key: key of the private value
        @param value: value to set
        @return: deferred"""
        d = self.dbpool.runQuery("REPLACE INTO private_gen(namespace,key,value) VALUES (?,?,?)", (namespace,key,value))
        d.addErrback(lambda ignore: error(_("Can't set general private value (%(key)s) [namespace:%(namespace)s] in database" % 
                     {"namespace":namespace, "key":key})))
        return d

    def setIndPrivate(self, namespace, key, value, profile):
        """Save the individual private value in database
        @param namespace: namespace of the value
        @param key: key of the private value
        @param value: value to set
        @param profile: a profile which *must* exist
        @return: deferred"""
        d = self.dbpool.runQuery("REPLACE INTO private_ind(namespace,key,profile_id,value) VALUES (?,?,?,?)", (namespace, key, self.profiles[profile], value))
        d.addErrback(lambda ignore: error(_("Can't set individual private value (%(key)s) [namespace: %(namespace)s] for [%(profile)s] in database" %
                     {"namespace":namespace, "key":key, "profile":profile})))
        return d

    def delGenPrivate(self, namespace, key):
        """Delete the general private value from database
        @param category: category of the privateeter
        @param key: key of the private value
        @return: deferred"""
        d = self.dbpool.runQuery("DELETE FROM private_gen WHERE namespace=? AND key=?", (namespace,key))
        d.addErrback(lambda ignore: error(_("Can't delete general private value (%(key)s) [namespace:%(namespace)s] in database" % 
                     {"namespace":namespace, "key":key})))
        return d

    def delIndPrivate(self, namespace, key, profile):
        """Delete the individual private value from database
        @param namespace: namespace of the value
        @param key: key of the private value
        @param profile: a profile which *must* exist
        @return: deferred"""
        d = self.dbpool.runQuery("DELETE FROM private_ind WHERE namespace=? AND key=? AND profile=?)", (namespace, key, self.profiles[profile]))
        d.addErrback(lambda ignore: error(_("Can't delete individual private value (%(key)s) [namespace: %(namespace)s] for [%(profile)s] in database" %
                     {"namespace":namespace, "key":key, "profile":profile})))
        return d


    def loadGenPrivatesBinary(self, private_gen, namespace):
        """Load general private binary values
        @param private_gen: dictionary to fill
        @param namespace: namespace of the values
        @return: deferred"""
        def fillPrivates(result):
            for private in result:
                key,value = private
                private_gen[key] = pickle.loads(str(value))
        debug(_("loading general private binary values [namespace: %s] from database") % (namespace,)) 
        d = self.dbpool.runQuery("SELECT key,value FROM private_gen_bin WHERE namespace=?", (namespace,)).addCallback(fillPrivates)
        return d.addErrback(lambda x: debug(_("No binary data present in database for namespace %s") % namespace))

    def loadIndPrivatesBinary(self, private_ind, namespace, profile):
        """Load individual private binary values
        @param privates_ind: dictionary to fill
        @param namespace: namespace of the values
        @param profile: a profile which *must* exist
        @return: deferred"""
        def fillPrivates(result):
            for private in result:
                key,value = private
                private_ind[key] = pickle.loads(str(value))
        debug(_("loading individual private binary values [namespace: %s] from database") % (namespace,))
        d = self.dbpool.runQuery("SELECT key,value FROM private_ind_bin WHERE namespace=? AND profile_id=?", (namespace, self.profiles[profile]))
        d.addCallback(fillPrivates)
        return d.addErrback(lambda x: debug(_("No binary data present in database for namespace %s") % namespace))

    def setGenPrivateBinary(self, namespace, key, value):
        """Save the general private binary value in database
        @param category: category of the privateeter
        @param key: key of the private value
        @param value: value to set
        @return: deferred"""
        d = self.dbpool.runQuery("REPLACE INTO private_gen_bin(namespace,key,value) VALUES (?,?,?)", (namespace,key,pickle.dumps(value,0)))
        d.addErrback(lambda ignore: error(_("Can't set general private binary value (%(key)s) [namespace:%(namespace)s] in database" % 
                     {"namespace":namespace, "key":key})))
        return d

    def setIndPrivateBinary(self, namespace, key, value, profile):
        """Save the individual private binary value in database
        @param namespace: namespace of the value
        @param key: key of the private value
        @param value: value to set
        @param profile: a profile which *must* exist
        @return: deferred"""
        d = self.dbpool.runQuery("REPLACE INTO private_ind_bin(namespace,key,profile_id,value) VALUES (?,?,?,?)", (namespace, key, self.profiles[profile], pickle.dumps(value,0)))
        d.addErrback(lambda ignore: error(_("Can't set individual binary private value (%(key)s) [namespace: %(namespace)s] for [%(profile)s] in database" %
                     {"namespace":namespace, "key":key, "profile":profile})))
        return d

    def delGenPrivateBinary(self, namespace, key):
        """Delete the general private binary value from database
        @param category: category of the privateeter
        @param key: key of the private value
        @return: deferred"""
        d = self.dbpool.runQuery("DELETE FROM private_gen_bin WHERE namespace=? AND key=?", (namespace,key))
        d.addErrback(lambda ignore: error(_("Can't delete general private binary value (%(key)s) [namespace:%(namespace)s] in database" % 
                     {"namespace":namespace, "key":key})))
        return d

    def delIndPrivateBinary(self, namespace, key, profile):
        """Delete the individual private binary value from database
        @param namespace: namespace of the value
        @param key: key of the private value
        @param profile: a profile which *must* exist
        @return: deferred"""
        d = self.dbpool.runQuery("DELETE FROM private_ind_bin WHERE namespace=? AND key=? AND profile=?)", (namespace, key, self.profiles[profile]))
        d.addErrback(lambda ignore: error(_("Can't delete individual private binary value (%(key)s) [namespace: %(namespace)s] for [%(profile)s] in database" %
                     {"namespace":namespace, "key":key, "profile":profile})))
        return d
    ##Helper methods##

    def __getFirstResult(self, result):
        """Return the first result of a database query
        Useful when we are looking for one specific value"""
        return None if not result else result[0][0]
