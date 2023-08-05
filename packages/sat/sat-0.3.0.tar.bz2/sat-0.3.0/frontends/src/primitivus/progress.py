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

import urwid
from urwid_satext import sat_widgets


class Progress(urwid.WidgetWrap):

    def __init__(self, host):
        self.host = host
        self.progress_list = urwid.SimpleListWalker([])
        self.progress_dict = {}
        listbox = urwid.ListBox(self.progress_list)
        buttons = []
        buttons.append(sat_widgets.CustomButton(_('Clear progress list'), self.__onClear))
        max_len = max([button.getSize() for button in buttons])
        buttons_wid = urwid.GridFlow(buttons,max_len,1,0,'center')
        main_wid = sat_widgets.FocusFrame(listbox, footer=buttons_wid)
        urwid.WidgetWrap.__init__(self, main_wid)

    def addProgress(self, progress_id, message):
        profile = self.host.profile # TODO: manage multiple profiles
        mess_wid = urwid.Text(message)
        progr_wid = urwid.ProgressBar('progress_normal', 'progress_complete')
        column = urwid.Columns([mess_wid, progr_wid])
        self.progress_dict[(progress_id, profile)] = {'full':column,'progress':progr_wid,'state':'init'}
        self.progress_list.append(column)
        self.progressCB(self.host.loop, (progress_id, message, profile))

    def progressCB(self, loop, data):
        progress_id, message, profile = data
        data = self.host.bridge.getProgress(progress_id, profile)
        pbar = self.progress_dict[(progress_id, profile)]['progress'] #FIXME: must manage profiles
        if data:
            if self.progress_dict[(progress_id, profile)]['state'] == 'init':
                #first answer, we must construct the bar
                self.progress_dict[(progress_id, profile)]['state'] = 'progress'
                pbar.done = float(data['size'])
                
            pbar.set_completion(float(data['position']))
            self.updateNotBar()
        else:
            if self.progress_dict[(progress_id, profile)]['state'] == 'progress':
                self.progress_dict[(progress_id, profile)]['state'] = 'done'
                pbar.set_completion(pbar.done)
                self.updateNotBar()
                return

        loop.set_alarm_in(1,self.progressCB, (progress_id, message, profile))

    def __removeBar(self, progress_id, profile):
        wid = self.progress_dict[(progress_id, profile)]['full']
        self.progress_list.remove(wid)
        del(self.progress_dict[(progress_id, profile)])

    def __onClear(self, button):
       to_remove = []
       for progress_id, profile in self.progress_dict:
           if self.progress_dict[(progress_id, profile)]['state'] == 'done':
               to_remove.append((progress_id, profile))
       for progress_id, profile in to_remove:
           self.__removeBar(progress_id, profile)
       self.updateNotBar()

    def updateNotBar(self):
        if not self.progress_dict:
            self.host.setProgress(None)
            return
        progress = 0
        nb_bars = 0
        for progress_id, profile in self.progress_dict:
            pbar = self.progress_dict[(progress_id, profile)]['progress']
            progress += pbar.current/pbar.done*100
            nb_bars+=1
        av_progress = progress/float(nb_bars)
        self.host.setProgress(av_progress)
    
