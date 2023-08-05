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
from curses import ascii
from window import Window

def C(k):
    """return the value of Ctrl+key"""
    return ord(ascii.ctrl(k))

def A(k):
    """return the value of Alt+key"""
    return ord(ascii.alt(k))

class EditBox(Window):
    """This class manage the edition of text"""

    def __init__(self, parent, header, code="utf-8"):
        self.__header=header
        self.__text = unicode()
        self.__curs_pos=0
        self.__buffer=str()
        self.__replace_mode=False
        self.__parent=parent
        self.__code=code
        
        Window.__init__(self, self.__parent, 1, self.__parent.getmaxyx()[1], self.__parent.getmaxyx()[0]-1,0, code=code)
        self.update()

    def registerEnterCB(self, CB):
        self.__enterCB=CB

    def resizeAdapt(self):
        """Adapt window size to self.__parent size.
        Must be called when self.__parent is resized."""
        self.resize(1, self.__parent.getmaxyx()[1], self.__parent.getmaxyx()[0]-1,0)
        self.update()

    def __getTextToPrint(self):
        """return the text printed on the edit line"""
        width = self.rWidth - len(self.__header) -1
        if self.__curs_pos<width:
            begin = 0 
            end = width
        else:
            begin = self.__curs_pos-width
            end = self.__curs_pos
        return self.__header+self.__text[begin:end]

    def update(self):
        Window.update(self)
        text = self.__getTextToPrint()
        self.addYXStr(0, 0, text, limit=self.rWidth)
        
        self.noutrefresh()

    def __dec_cur(self):
        """move cursor on the left"""
        if self.__curs_pos>0:
            self.__curs_pos = self.__curs_pos - 1

    def __inc_cur(self):
        """move cursor on the right"""
        if self.__curs_pos<len(self.__text):
            self.__curs_pos = self.__curs_pos + 1
    
    def move_cur(self, x):
        pos = x+len(self.__header)
        if pos>=self.rWidth:
            pos=self.rWidth-1
        self.move(0, pos)

    def clear_text(self):
        """Clear the text of the edit box"""
        self.__text=""
        self.__curs_pos=0
        
    def replace_cur(self):
        """must be called earch time the cursor is moved"""
        self.move_cur(self.__curs_pos)
        self.noutrefresh()

    def activate(self, state=True):
        cursor_mode = 1 if state else 0
        curses.curs_set(cursor_mode)
        Window.activate(self,state)

    def handleKey(self, k):
        if ascii.isgraph(k) or ascii.isblank(k):
            pacman = 0 if not self.__replace_mode else 1
            self.__text = self.__text[:self.__curs_pos] + chr(k) + self.__text[self.__curs_pos + pacman:]
            self.__curs_pos = self.__curs_pos + 1

        elif k==ascii.NL:
            try:
                self.__enterCB(self.__text)
            except NameError:
                pass # TODO: thrown an error here
            self.clear_text()

        elif k==curses.KEY_BACKSPACE:
            self.__text = self.__text[:self.__curs_pos-1]+self.__text[self.__curs_pos:]
            self.__dec_cur()

        elif k==curses.KEY_DC:
            self.__text = self.__text[:self.__curs_pos]+self.__text[self.__curs_pos+1:]

        elif k==curses.KEY_IC:
            self.__replace_mode = not self.__replace_mode

        elif k==curses.KEY_LEFT:
            self.__dec_cur()

        elif k==curses.KEY_RIGHT:
            self.__inc_cur()

        elif k==curses.KEY_HOME or k==C('a'):
            self.__curs_pos=0
        
        elif k==curses.KEY_END or k==C('e'):
            self.__curs_pos=len(self.__text)

        elif k==C('k'):
            self.__text = self.__text[:self.__curs_pos]

        elif k==C('w'):
            before = self.__text[:self.__curs_pos]
            pos = before.rstrip().rfind(" ")+1
            self.__text = before[:pos] + self.__text[self.__curs_pos:]
            self.__curs_pos = pos

        elif k>255:
            self.__buffer=""

        else:  ## FIXME: dangerous code, must be checked ! (specialy buffer overflow) ##
            #We now manage unicode
            self.__buffer = self.__buffer+chr(k)
            decoded=unicode()
            if len(self.__buffer)>4:
                self.__buffer=""
                return
            try:
                decoded = self.__buffer.decode(self.__code)
            except UnicodeDecodeError, e:
                if e.reason!="unexpected end of data":
                    self.__buffer=""
                return
            if len(self.__buffer)==1:  ## FIXME: awful ! only for test !
                self.__buffer=""
                return
            self.__text = self.__text + decoded
            self.__curs_pos = self.__curs_pos + 1
            self.__buffer=""

        self.update()

