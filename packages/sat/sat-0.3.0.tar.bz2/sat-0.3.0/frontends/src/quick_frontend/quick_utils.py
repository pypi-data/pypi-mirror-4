#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Primitivus: a SAT frontend
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

from sat.tools.jid  import JID
from os.path import exists, splitext

def escapePrivate(ori_jid):
    """Escape a private jid"""
    return JID(const_PRIVATE_PREFIX + ori_jid.short + '@' + ori_jid.resource)

def unescapePrivate(escaped_jid):
    if not escaped_jid.startswith(const_PRIVATE_PREFIX):
        return escaped_jid
    escaped_split = tuple(escaped_jid[len(const_PRIVATE_PREFIX):].split('@'))
    assert(len(escaped_split) == 3)
    return JID("%s@%s/%s" % escaped_split)

def getNewPath(path):
    """ Check if path exists, and find a non existant path if needed """
    idx = 2
    if not exists(path):
        return path
    root, ext = splitext(path)
    while True:
        new_path = "%s_%d%s" % (root, idx, ext)
        if not exists(new_path):
            return new_path
        idx+=1

