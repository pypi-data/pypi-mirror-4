#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SAT plugin for managing xep-0020
Copyright (C) 2009, 2010, 2011, 2012, 2013 Jérôme Poisson (goffi@goffi.org)

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

from logging import debug, info, warning, error
from twisted.words.protocols.jabber import client, jid
from twisted.words.xish import domish

from zope.interface import implements

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

from wokkel import disco, iwokkel, data_form

NS_FEATURE_NEG = 'http://jabber.org/protocol/feature-neg'

PLUGIN_INFO = {
"name": "XEP 0020 Plugin",
"import_name": "XEP-0020",
"type": "XEP",
"protocols": ["XEP-0020"],
"main": "XEP_0020",
"handler": "yes",
"description": _("""Implementation of Feature Negotiation""")
}

class XEP_0020():

    def __init__(self, host):
        info(_("Plugin XEP_0020 initialization"))
    
    def getHandler(self, profile):
        return XEP_0020_handler()

    def getFeatureElt(self, elt):
        """Check element's children to find feature elements
        @param elt: domish.Element
        @return: feature elements"""
        return filter(lambda elt: elt.name == 'feature', elt.elements())

    def getChoosedOptions(self, elt):
        """Return choosed feature for feature element
        @param elt: feature domish element
        @return: dict with feature name as key, and choosed option as value"""
        form = data_form.Form.fromElement(elt.firstChildElement())
        result = {}
        for field in form.fields:
            values = form.fields[field].values
            result[field] = values[0] if values else None
            if len(values)>1:
                warning(_("More than one value choosed for %s, keeping the first one") % field)
        return result

    def negociate(self, feature_elt, form_type, negociable_values):
        """Negociate the feature options
        @param feature_elt: feature domish element
        @param form_type: the option to negociate
        @param negociable_values: acceptable values for this negociation"""
        form = data_form.Form.fromElement(feature_elt.firstChildElement())
        options = [option.value for option in form.fields[form_type].options]
        for value in negociable_values:
            if value in options:
                return value
        return None

    def chooseOption(self, options_dict):
        """Build a feature element with choosed options
        @param options_dict: dict with feature as key and choosed option as value"""
        feature_elt = domish.Element((NS_FEATURE_NEG, 'feature'))
        x_form = data_form.Form('submit')
        x_form.makeFields(options_dict)
        feature_elt.addChild(x_form.toElement())
        return feature_elt

    def proposeFeatures(self, options_dict, namespace = None):
        """Build a feature element with options to propose
        @param options_dict: dict with feature as key and list of acceptable options as value
        @param namespace: feature namespace"""
        feature_elt = domish.Element((NS_FEATURE_NEG, 'feature'))
        x_form = data_form.Form('form', formNamespace=namespace)
        for field in options_dict:
            x_form.addField(data_form.Field('list-single', field,
                            options=[data_form.Option(_option) for _option in options_dict[field]]))
        feature_elt.addChild(x_form.toElement())
        return feature_elt

class XEP_0020_handler(XMPPHandler):
    implements(iwokkel.IDisco)
    
    def getDiscoInfo(self, requestor, target, nodeIdentifier=''):
        return [disco.DiscoFeature(NS_FEATURE_NEG)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=''):
        return []

