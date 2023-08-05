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


from window import Window
import os,pdb

class BoxSizer:
    """This class manage the position of the window like boxes."""



    def __init__(self, parent):
        self.__parent=parent
        self.boxes=[]



    def appendRow(self, win):
        self.boxes.append([win])

    def appendColum(self, index, win):
        if len(self.boxes)<=index:
            #TODO: throw an error here
            return
        self.boxes[index].append(win)

    def update(self):
        """Resize boxes"""
        oriY=0
        visible_row=[]
        for row in self.boxes:
            current_row=[]
            oriX=0
            for win in row:
                x=win.getOriX()
                y=win.getOriY()
                w=win.getOriWidth()
                h=win.getOriHeight()
                if win.isHidden():
                    if len(current_row)>1 and win is row[-1]:
                        #if the last win is hidden, we expand previous visible one
                        current_row[-1][2] = current_row[-1][2] + (win.getX() - oriX)+win.getWidth()
                else:
                    current_row.append([win, h+y-oriY, w+x-oriX, oriY, oriX])
                    oriX=oriX+w
                    
            if oriX!=0:
                oriY=oriY+h
                visible_row.append(current_row)
            elif visible_row:
                #if all the row is empty, we take the space
                for box in visible_row[-1]:
                    box[1]=box[1]+h
                oriY=oriY+h  #this only happen if it's not the first visible row

        for row in visible_row:
            for win in row:
                win[0].resize(win[1], win[2], win[3], win[4])
