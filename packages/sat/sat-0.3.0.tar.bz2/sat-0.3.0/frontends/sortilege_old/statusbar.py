#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
sortilege: a SAT frontend
Copyright (C) 2009, 2010, 2011  Jérôme Poisson (goffi@goffi.org)

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


import curses
from window import Window
import os

class StatusBar(Window):
    """This class manage the edition of text"""

    def __init__(self, parent, code="utf-8"):
        self.__parent=parent
        self.__code=code
        self.__items=set()
        
        Window.__init__(self, self.__parent, 1, self.__parent.getmaxyx()[1], self.__parent.getmaxyx()[0]-2,0, code=code)

    def __len__(self):
        return len(self.__items)

    def resizeAdapt(self):
        """Adapt window size to self.__parent size.
        Must be called when self.__parent is resized."""
        self.resize(1, self.__parent.getmaxyx()[1], self.__parent.getmaxyx()[0]-2,0)
        self.update()

    def update(self):
        if self.isHidden():
            return
        Window.update(self)
        x=0
        for item in self.__items:
            pitem="[%s] " % item
            self.addYXStr(0, x, pitem, curses.A_REVERSE)
            x = x + len(pitem)
            if x>=self.rWidth:
                break
        self.addYXStr(0, x, (self.rWidth-x)*" ", curses.A_REVERSE)
        self.noutrefresh()

    def clear_text(self):
        """Clear the text of the edit box"""
        del(self.__items[:])
       
    def add_item(self, item):
        self.__items.add(item)
        self.update()
       
    def remove_item(self, item):
        if item in self.__items:
            self.__items.remove(item)
        self.update()
