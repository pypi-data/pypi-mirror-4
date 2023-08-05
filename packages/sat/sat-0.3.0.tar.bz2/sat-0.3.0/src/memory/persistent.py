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

class MemoryNotInitializedError(Exception):
    pass

class PersistentDict:
    """A dictionary which save persistently each value assigned
    /!\ be careful, each assignment means a database write
    /!\ Memory must be initialised before loading/setting value with instances of this class"""
    storage = None

    def __init__(self, namespace, profile=None):
        """@param namespace: unique namespace for this dictionary
        @param profile: profile which *MUST* exists, or None for general values"""
        if not self.storage:
            error(_("PersistentDict can't be used before memory initialisation"));
            raise MemoryNotInitializedError
        self._cache = {}
        self.namespace = namespace
        self.profile = profile

    def load(self):
        """load persistent data from storage
        """
        if not self.profile:
            return self.storage.loadGenPrivates(self._cache, self.namespace)
        else:
            return self.storage.loadIndPrivates(self._cache, self.namespace, self.profile)

    def __repr__(self):
        return self._cache.__repr__()

    def __str__(self):
        return self._cache.__str__()

    def __lt__(self, other):
        return self._cache.__lt__(other)

    def __le__(self, other):
        return self._cache.__le__(other)

    def __eq__(self, other):
        return self._cache.__eq__(other)

    def __ne__(self, other):
        return self._cache.__ne__(other)

    def __gt__(self, other):
        return self._cache.__gt__(other)

    def __ge__(self, other):
        return self._cache.__ge__(other)

    def __cmp__(self, other):
        return self._cache.__cmp__(other)
    
    def __hash__(self):
        return self._cache.__hash__()

    def __nonzero__(self):
        return self._cache.__len__()

    def __unicode__(self):
        return self._cache.__unicode__()

    def __contains__(self, key):
        return self._cache.__contains__(key)

    def __getitem__(self, key):
        return self._cache.__getitem__(key)

    def __setitem__(self, key, value):
        if not self.profile:
            self.storage.setGenPrivate(self.namespace, key, value)
        else:
            self.storage.setIndPrivate(self.namespace, key, value, self.profile)
        return self._cache.__setitem__(key, value)

    def __delitem__(self, key):
        if not self.profile:
            self.storage.delGenPrivate(self.namespace, key)
        else:
            self.storage.delIndPrivate(self.namespace, key, self.profile)
        return self._cache.__delitem__(key)

    def get(self, key, default=None):
        return self._cache.get(key, default)

    def force(self, name):
        """Force saving of an attribute to storage
        @return: deferred fired when data is actually saved"""
        if not self.profile:
            return self.storage.setGenPrivate(self.namespace, name, self._cache[name])
        return self.storage.setIndPrivate(self.namespace, name, self._cache[name], self.profile)


class PersistentBinaryDict(PersistentDict):
    """Persistent dict where value can be any python data (instead of string only)"""
    
    def load(self):
        """load persistent data from storage
        """
        if not self.profile:
            return self.storage.loadGenPrivatesBinary(self._cache, self.namespace)
        else:
            return self.storage.loadIndPrivatesBinary(self._cache, self.namespace, self.profile)

    def __setitem__(self, key, value):
        if not self.profile:
            self.storage.setGenPrivateBinary(self.namespace, key, value)
        else:
            self.storage.setIndPrivateBinary(self.namespace, key, value, self.profile)
        return self._cache.__setitem__(key, value)

    def __delitem__(self, key):
        if not self.profile:
            self.storage.delGenPrivateBinary(self.namespace, key)
        else:
            self.storage.delIndPrivateBinary(self.namespace, key, self.profile)
        return self._cache.__delitem__(key)

    def force(self, name):
        """Force saving of an attribute to storage
        @return: deferred fired when data is actually saved"""
        if not self.profile:
            return self.storage.setGenPrivateBinary(self.namespace, name, self._cache[name])
        return self.storage.setIndPrivateBinary(self.namespace, name, self._cache[name], self.profile)

