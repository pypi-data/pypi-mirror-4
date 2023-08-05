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
import os
import pdb


class Window():
    def __init__(self, parent, height, width, y, x, border=False, title="", code="utf-8"):
        self.__border=border
        self.__title=title
        self.__active=False
        self.__parent=parent
        self.__code=code
        self.__hide=False
        
        self.resize(height, width, y, x)
        self.oriCoords=self.__coords #FIXME: tres moche, a faire en mieux

    def hide(self, hide=True):
        self.__hide=hide

    def show(self):
        self.__hide=False

    def isHidden(self):
        return self.__hide

    def getY(self):
        return self.__coords[2]

    def getX(self):
        return self.__coords[3]

    def getHeight(self):
        return self.__coords[0]

    def getWidth(self):
        return self.__coords[1]


    #FIXME: tres moche, a faire en plus joli
    def getOriY(self):
        return self.oriCoords[2]

    def getOriX(self):
        return self.oriCoords[3]

    def getOriHeight(self):
        return self.oriCoords[0]

    def getOriWidth(self):
        return self.oriCoords[1]

    def defInsideCoord(self):
        """define the inside coordinates (win coordinates minus decorations)"""
        height,width,y,x=self.__coords
        self.oriX = x if not self.__border else x+1
        self.oriY = y if not self.__border else y+1
        self.endX = x+width if not self.__border else x+width-2
        self.endY = y+height if not self.__border else y+height-2
        self.rWidth = width if not self.__border else width-2
        self.rHeight = height if not self.__border else height-2

    def resize(self, height, width, y, x):
        self.__coords=[height, width, y, x]

        # we check that coordinates are under limits
        self.__coordAdjust(self.__coords)
        height,width,y,x=self.__coords
       
        self.window = self.__parent.subwin(height, width, y, x)
        self.defInsideCoord()

    def __coordAdjust(self, coords):
        """Check that coordinates are under limits, adjust them else otherwise"""
        height,width,y,x=coords
        parentY, parentX = self.__parent.getbegyx()
        parentHeight, parentWidth = self.__parent.getmaxyx()

        if y < parentY:
            y = parentY
        if x < parentX:
            x = parentX
        if height > parentHeight - y:
            height = parentHeight - y
        if width > parentWidth - x:
            width = parentWidth - x
        coords[0], coords[1], coords[2], coords[3] = [height, width, y, x]


    def activate(self,state=True):
        """Declare this window as current active one"""
        self.__active=state
        self.update()

    def isActive(self):
        return self.__active

    def addYXStr(self, y, x, text, attr = 0, limit=0):
        if self.__border:
            x=x+1
            y=y+1
        n = self.rWidth-x if not limit else limit
        encoded = text.encode(self.__code)
        adjust = len(encoded) - len(text) # hack because addnstr doesn't manage unicode
        try:    
            self.window.addnstr(y, x, encoded, n + adjust, attr) 
        except:
            #We have to catch error to write on last line last col FIXME: is there a better way ?
            pass

    def move(self, y, x):
        self.window.move(y,x)
    
    def noutrefresh(self):
        self.window.noutrefresh()

    def update(self):
        """redraw all the window"""
        if self.__hide:
            return
        self.clear()

    def border(self):
        """redraw the border and title"""
        y,x = self.window.getbegyx()
        width = self.window.getmaxyx()[1]
        if self.__border:
            self.window.border()
            if self.__title:
                if len(self.__title)>width:
                    self.__title=""
                else:
                    self.window.addstr(y,x+(width-len(self.__title))/2, self.__title)

    def clear(self):
        self.window.clear()
        self.border()
