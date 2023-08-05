import sys,os.path
import __builtin__
import sat_frontends.wix

wix_root = os.path.dirname(sat_frontends.wix.__file__)

__builtin__.__dict__['APP_NAME'] = "Wix"
__builtin__.__dict__['LICENCE_PATH'] = os.path.join(wix_root,"COPYING")

__builtin__.__dict__['msgOFFLINE']          = _("offline")
__builtin__.__dict__['msgONLINE']           = _("online")
__builtin__.__dict__['const_DEFAULT_GROUP'] = "Unclassed"
__builtin__.__dict__['const_STATUS']        = [("", _("Online"), None),
                                               ("chat", _("Free for chat"), "green"),
                                               ("away", _("AFK"), "brown"),
                                               ("dnd", _("DND"), "red"),
                                               ("xa", _("Away"), "red")]
