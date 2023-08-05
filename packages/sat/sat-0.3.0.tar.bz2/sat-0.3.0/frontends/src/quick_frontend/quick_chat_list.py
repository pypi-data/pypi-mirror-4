#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
helper class for making a SAT frontend
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


class QuickChatList(dict):
    """This class is used to manage the list of chat windows.
    It act as a dict, but create a chat window when the name is found for the first time."""
    
    def __init__(self, host):
        dict.__init__(self)
        self.host = host

    def __getitem__(self,to_jid):
        target=JID(to_jid)
        if not self.has_key(target.short):
            #we have to create the chat win
            self[target.short] = self.createChat(target)
        return dict.__getitem__(self,target.short)

    def createChat(self, target):
        raise NotImplementedError
