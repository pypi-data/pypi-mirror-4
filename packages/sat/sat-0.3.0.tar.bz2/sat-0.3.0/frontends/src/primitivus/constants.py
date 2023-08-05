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
import __builtin__

__builtin__.__dict__['const_APP_NAME'] = "Primitivus"
__builtin__.__dict__['const_PALETTE']  = [
    ('title', 'black', 'light gray', 'standout,underline'),
    ('title_focus', 'white,bold', 'light gray', 'standout,underline'),
    ('selected', 'default', 'dark red'),
    ('selected_focus', 'default,bold', 'dark red'),
    ('default', 'default', 'default'),
    ('default_focus', 'default,bold', 'default'),
    ('alert', 'default,underline', 'default'),
    ('alert_focus', 'default,bold,underline', 'default'),
    ('date', 'light gray', 'default'),
    ('my_nick', 'dark red,bold', 'default'),
    ('other_nick', 'dark cyan,bold', 'default'),
    ('menubar', 'light gray,bold', 'dark red'),
    ('menubar_focus', 'light gray,bold', 'dark green'),
    ('selected_menu', 'light gray,bold', 'dark green'),
    ('menuitem', 'light gray,bold', 'dark red'),
    ('menuitem_focus', 'light gray,bold', 'dark green'),
    ('notifs', 'black,bold', 'yellow'),
    ('notifs_focus', 'dark red', 'yellow'),
    ('card_neutral', 'dark gray', 'white', 'standout,underline'),
    ('card_neutral_selected', 'dark gray', 'dark green', 'standout,underline'),
    ('card_special', 'brown', 'white', 'standout,underline'),
    ('card_special_selected', 'brown', 'dark green', 'standout,underline'),
    ('card_red', 'dark red', 'white', 'standout,underline'),
    ('card_red_selected', 'dark red', 'dark green', 'standout,underline'),
    ('card_black', 'black', 'white', 'standout,underline'),
    ('card_black_selected', 'black', 'dark green', 'standout,underline'),
    ('directory', 'dark cyan, bold', 'default'),
    ('directory_focus', 'dark cyan, bold', 'dark green'),
    ('separator', 'brown', 'default'),
    ('warning', 'light red', 'default'),
    ('progress_normal', 'default', 'black'),
    ('progress_complete', 'default', 'light red'),
    ('show_disconnected', 'dark gray', 'default'),
    ('show_normal', 'default', 'default'),
    ('show_normal_focus', 'default, bold', 'default'),
    ('show_chat', 'dark green', 'default'),
    ('show_chat_focus', 'dark green, bold', 'default'),
    ('show_away', 'brown', 'default'),
    ('show_away_focus', 'brown, bold', 'default'),
    ('show_dnd', 'dark red', 'default'),
    ('show_dnd_focus', 'dark red, bold', 'default'),
    ('show_xa', 'dark red', 'default'),
    ('show_xa_focus', 'dark red, bold', 'default'),
    ('status', 'yellow', 'default'),
    ('status_focus', 'yellow, bold', 'default'),
    ]
__builtin__.__dict__['const_SHOW_ICON'] = {"unavailable": (u'⨯', "show_disconnected"), 
                                          "": (u'✔', "show_normal"),
                                          "chat": (u'✆', "show_chat"),
                                          "away": (u'✈', "show_away"),
                                          "dnd": (u'✖', "show_dnd"),
                                          "xa": (u'☄', "show_xa")}
