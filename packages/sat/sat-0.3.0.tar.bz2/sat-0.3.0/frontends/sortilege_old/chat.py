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



import os.path
import pdb
from logging import debug, info, error
from window import Window
import os
from time import time, localtime, strftime
import curses
import curses.ascii as ascii
from tools.jid  import JID
from quick_frontend.quick_chat import QuickChat


def C(k):
    """return the value of Ctrl+key"""
    return ord(ascii.ctrl(k))

class Chat(Window, QuickChat):

    def __init__(self, to_id, host):
        QuickChat.__init__(self, to_id, host) 
        self.__parent=host.stdscr
        self.to_id=JID(to_id)
        self.content=[]
        self.__scollIdx=0
        Window.__init__(self, self.__parent, self.__parent.getmaxyx()[0]-2, self.__parent.getmaxyx()[1]-30, 0,30, code=host.code)

        #history
        self.historyPrint(50, True, profile=self.host.profile)

        self.hide()

    def resize(self, height, width, y, x):
        Window.resize(self, height, width, y, x)
        self.update()

    def resizeAdapt(self):
        """Adapt window size to self.__parent size.
        Must be called when self.__parent is resized."""
        self.resize(self.__parent.getmaxyx()[0]-2, self.__parent.getmaxyx()[1]-30, 0,30)
        self.update()

    def __getHeader(self, line):
        """Return the header of a line (eg: "[12:34] <toto> ")."""
        header=''
        if self.host.chatParams["timestamp"]:
            header = header + '[%s] ' % strftime("%H:%M", localtime(float(line[0])))
        if self.host.chatParams['short_nick']:
            header = header + ('> ' if  line[1]==self.host.profiles[self.host.profile]['whoami'] else '** ')
        else:
            header = header + '<%s> ' % line[1]
        return header

    def update(self):
        if self.isHidden():
            return
        Window.update(self)
        content=[] #what is really printed
        irange=range(len(self.content))
        irange.reverse() #we print the text upward
        for idx in irange:
            header=self.__getHeader(self.content[idx])
            msg=self.content[idx][2]
            part=0  #part of the text
            if JID(self.content[idx][1]).short==self.host.profiles[self.host.profile]['whoami'].short:
                att_header=curses.color_pair(1)
            else:
                att_header=curses.color_pair(2)
            
            while (msg):
                if part==0:
                    hd=header
                    att=att_header
                    max=self.rWidth-len(header)
                else:
                    hd=""
                    att=0
                    max=self.rWidth

                LF = msg.find('\n')   #we look for Line Feed
                if LF != -1 and LF < max:
                    max = LF
                    next = max + 1  #we skip the LF
                else:
                    next = max
                    
                content.insert(part,[att,hd, msg[:max]])
                msg=msg[next:]   #we erase treated part
                part=part+1

            if len(content)>=self.rHeight+self.__scollIdx:
                #all the screen is filled, we can continue
                break

        if self.__scollIdx>0 and len(content)<self.rHeight+self.__scollIdx:
            self.__scollIdx=abs(len(content)-self.rHeight)  #all the log fit on the screen, we must stop here
            
        idx=0
        for line in content[-self.rHeight-self.__scollIdx : -self.__scollIdx or None]:
            self.addYXStr(idx, 0, line[1], line[0])
            self.addYXStr(idx, len(line[1]), line[2])
            idx=idx+1

        self.noutrefresh()
    
    def scrollIdxUp(self):
        """increment scroll index"""
        self.__scollIdx = self.__scollIdx + 1
        self.update()
    
    def scrollIdxDown(self):
        """decrement scroll index"""
        if self.__scollIdx > 0:
            self.__scollIdx = self.__scollIdx - 1
        self.update()

    def printMessage(self, jid, msg, profile, timestamp=""):
        if timestamp=="":
            current_time=time()
            timestamp=str(current_time)
            if self.last_history and current_time - float(self.last_history) < 5: #FIXME: Q&D fix to avoid double print on new chat window
                return
        self.content.append([timestamp,jid.short,msg])
        self.update()
    
    def handleKey(self, k):
        if k == C('p'):
            self.scrollIdxUp()
        elif k == C('n'):
            self.scrollIdxDown()

