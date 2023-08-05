#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
SAT: a jabber client
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


#consts
NAME = u"bridge_constructor"
VERSION="0.1.0"
DEST_DIR="generated"
ABOUT = NAME+u""" v%s (c) Jérôme Poisson (aka Goffi) 2011

---
"""+NAME+u""" Copyright (C) 2011  Jérôme Poisson (aka Goffi)
This program comes with ABSOLUTELY NO WARRANTY;
This is free software, and you are welcome to redistribute it
under certain conditions.
---

This script construct a SàT bridge using the given protocol
"""
MANAGED_PROTOCOLES=['dbus','mediawiki', 'dbus-xml']
DEFAULT_PROTOCOLE='dbus'
FLAGS=['deprecated', 'async']

ENV_OVERRIDE = "SAT_BRIDGE_CONST_" #Prefix used to override a constant

import sys
import os
from os import path
from optparse import OptionParser
from ConfigParser import SafeConfigParser as Parser
from ConfigParser import NoOptionError
import re
from datetime import datetime
from xml.dom import minidom


class ParseError(Exception):
    #Used when the signature parsing is going wrong (invalid signature ?) 
    pass

class Constructor:
    
    def __init__(self, bridge_template, options):
        self.bridge_template = bridge_template
        self.options = options

    def getValues(self, name):
        """Return values of a function in a dict
        @param name: Name of the function to get
        @return: dict, each key has the config value or None if the value is not set"""
        function={}
        for option in ['type','category','sig_in','sig_out','doc']:
            try:
                value = self.bridge_template.get(name, option)
            except NoOptionError:
                value = None
            function[option] = value
        return function
    
    def getDefault(self, name):
        """Return default values of a function in a dict
        @param name: Name of the function to get
        @return: dict, each key is the integer param number (no key if no default value)"""
        default_dict={}
        def_re = re.compile(r"param_(\d+)_default")
        
        for option in self.bridge_template.options(name):
            match = def_re.match(option)
            if match:
                try:
                    idx = int(match.group(1))
                except ValueError:
                    raise ParseError("Invalid value [%s] for parameter number" % match.group(1))
                default_dict[idx] = self.bridge_template.get(name, option)
        
        return default_dict

    def getFlags(self, name):
        """Return list of flags set for this function
        @param name: Name of the function to get
        @return: List of flags (string)"""
        flags=[]
        for option in self.bridge_template.options(name):
            if option in FLAGS:
                flags.append(option)
        return flags
    
    def getArgumentsDoc(self, name):
        """Return documentation of arguments
        @param name: Name of the function to get
        @return: dict, each key is the integer param number (no key if no argument doc), value is a tuple (name, doc)"""
        doc_dict={}
        option_re = re.compile(r"doc_param_(\d+)")
        value_re = re.compile(r"^(\w+): (.*)$", re.MULTILINE | re.DOTALL)
        for option in self.bridge_template.options(name):
            if option == 'doc_return':
                doc_dict['return'] = self.bridge_template.get(name, option)
                continue
            match = option_re.match(option)
            if match:
                try:
                    idx = int(match.group(1))
                except ValueError:
                    raise ParseError("Invalid value [%s] for parameter number" % match.group(1))
                value_match = value_re.match(self.bridge_template.get(name, option))
                if not value_match:
                    raise ParseError("Invalid value for parameter doc [%i]" % idx)
                doc_dict[idx]=(value_match.group(1),value_match.group(2))
        return doc_dict

    def getDoc(self, name):
        """Return documentation of the method
        @param name: Name of the function to get
        @return: string documentation, or None"""
        if self.bridge_template.has_option(name, "doc"):
            return self.bridge_template.get(name, "doc")
        return None


    def argumentsParser(self, signature):
        """Generator which return individual arguments signatures from a global signature"""
        start=0
        i=0

        while i<len(signature):
            if signature[i] not in ['b','y','n','i','x','q','u','t','d','s','a']:
                raise ParseError("Unmanaged attribute type [%c]" % signature[i])

            if signature[i] == 'a':
                i+=1
                if signature[i]!='{' and signature[i]!='(': #FIXME: must manage tuples out of arrays
                    i+=1
                    yield signature[start:i]
                    start=i
                    continue #we have a simple type for the array
                opening_car = signature[i]
                assert(opening_car in ['{','('])
                closing_car = '}' if opening_car == '{' else ')'
                opening_count = 1
                while (True): #we have a dict or a list of tuples
                    i+=1
                    if i>=len(signature):
                        raise ParseError("missing }")
                    if signature[i] == opening_car:
                        opening_count+=1
                    if signature[i] == closing_car:
                        opening_count-=1
                        if opening_count == 0:
                            break
            i+=1
            yield signature[start:i]
            start=i

    def getArguments(self, signature, name=None, default=None, unicode_protect=False):
        """Return arguments to user given a signature
        @param signature: signature in the short form (using s,a,i,b etc)
        @param name: dictionary of arguments name like given by getArguments
        @param default: dictionary of default values, like given by getDefault
        @param unicode_protect: activate unicode protection on strings (return strings as unicode(str))
        @return: list of arguments that correspond to a signature (e.g.: "sss" return "arg1, arg2, arg3")""" 
        idx=0
        attr_string=[]
        
        for arg in self.argumentsParser(signature):
            attr_string.append(("unicode(%(name)s)%(default)s" if (unicode_protect and arg=='s') else "%(name)s%(default)s") % {
                'name':name[idx][0] if (name and name.has_key(idx)) else "arg_%i" % idx,
                'default':"="+default[idx] if (default and default.has_key(idx)) else ''
                }) #give arg_1, arg2, etc or name1, name2=default, etc. \
                   #give unicode(arg_1), unicode(arg_2), etc. if unicode_protect is set and arg is a string
            idx+=1
        
        return ", ".join(attr_string)

    def generateCoreSide(self):
        """create the constructor in SàT core side (backend)"""
        raise NotImplementedError

    def generateFrontendSide(self):
        """create the constructor in SàT frontend side"""
        raise NotImplementedError

    def finalWrite(self, filename, file_buf):
        """Write the final generated file in DEST_DIR/filename
        @param filename: name of the file to generate
        @param file_buf: list of lines (stings) of the file"""
        if os.path.exists(DEST_DIR) and not os.path.isdir(DEST_DIR):
            print ("The destination dir [%s] can't be created: a file with this name already exists !")
            sys.exit(1)
        try:
            if not os.path.exists(DEST_DIR):
                os.mkdir(DEST_DIR)
            full_path=os.path.join(DEST_DIR,filename)
            if os.path.exists(full_path) and not self.options.force:
                print ("The destination file [%s] already exists ! Use --force to overwrite it" % full_path) 
            try:
                with open(full_path,'w') as dest_file:
                    dest_file.write('\n'.join(file_buf))
            except IOError:
                print ("Can't open destination file [%s]" % full_path)
        except OSError:
            print("It's not possible to generate the file, check your permissions")
            exit(1)

class MediawikiConstructor(Constructor):

    def __init__(self, bridge_template, options):
        Constructor.__init__(self, bridge_template, options)
        self.core_template="mediawiki_template.tpl" 
        self.core_dest="mediawiki.wiki" 

    def _addTextDecorations(self, text):
        """Add text decorations like coloration or shortcuts"""

        def anchor_link(match):
            link = match.group(1)
            #we add anchor_link for [method_name] syntax:
            if link in self.bridge_template.sections():
                return "[[#%s|%s]]" % (link, link)
            print ("WARNING: found an anchor link to an unknown method")
            return link

        return re.sub(r"\[(\w+)\]", anchor_link, text)

    def _wikiParameter(self, name, sig_in):
        """Format parameters with the wiki syntax
        @param name: name of the function
        @param sig_in: signature in
        @return: string of the formated parameters"""
        arg_doc = self.getArgumentsDoc(name)
        arg_default = self.getDefault(name)
        args_str = self.getArguments(sig_in)
        args = args_str.split(', ') if args_str else [] #ugly but it works :)
        wiki=[]
        for i in range(len(args)):
            if arg_doc.has_key(i):
                name,doc=arg_doc[i]
                doc='\n:'.join(doc.rstrip('\n').split('\n'))
                wiki.append("; %s: %s" % (name, self._addTextDecorations(doc)))
            else:
                wiki.append("; arg_%d: " % i)
            if arg_default.has_key(i):
                wiki.append(":''DEFAULT: %s''" % arg_default[i])
        return "\n".join(wiki)
         
    def _wikiReturn(self, name):
        """Format return doc with the wiki syntax
        @param name: name of the function
        """
        arg_doc = self.getArgumentsDoc(name)
        wiki=[]
        if arg_doc.has_key('return'):
            wiki.append('\n|-\n! scope=row | return value\n|')
            wiki.append('<br />\n'.join(self._addTextDecorations(arg_doc['return']).rstrip('\n').split('\n')))
        return "\n".join(wiki)

    def generateCoreSide(self):
        signals_part = []
        methods_part = []
        sections = self.bridge_template.sections()
        sections.sort()
        for section in sections:
            function = self.getValues(section)
            print ("Adding %s %s" % (section, function["type"]))
            default = self.getDefault(section)
            async_msg = """<br />'''This method is asynchronous'''"""
            deprecated_msg = """<br />'''<font color="#FF0000">/!\ WARNING /!\ : This method is deprecated, please don't use it !</font>'''"""
            signature_signal = \
"""\
! scope=row | signature
| %s
|-\
""" % function['sig_in']
            signature_method = \
"""\
! scope=row | signature in
| %s
|-
! scope=row | signature out
| %s
|-\
""" % (function['sig_in'], function['sig_out'])
            completion = {
                'signature':signature_signal if function['type']=="signal" else signature_method,
                'sig_out':function['sig_out'] or '',
                'category':function['category'],
                'name':section,
                'doc':self.getDoc(section) or "FIXME: No description available",
                'async':async_msg if "async" in self.getFlags(section) else "",
                'deprecated':deprecated_msg if "deprecated" in self.getFlags(section) else "",
                'parameters':self._wikiParameter(section, function['sig_in']),
                'return':self._wikiReturn(section) if function['type'] == 'method' else ''
                }

            dest = signals_part if function['type'] == "signal" else methods_part
            dest.append("""\
== %(name)s ==
''%(doc)s''
%(deprecated)s
%(async)s
{| class="wikitable" style="text-align:left; width:80%%;"
! scope=row | category
| %(category)s 
|-
%(signature)s
! scope=row | parameters
|
%(parameters)s%(return)s
|}
""" % completion)
        
        #at this point, signals_part, and methods_part should be filled,
        #we just have to place them in the right part of the template
        core_bridge = []
        try:
            with open(self.core_template) as core_template:
                for line in core_template:
                    if line.startswith('##SIGNALS_PART##'):
                        core_bridge.extend(signals_part)
                    elif line.startswith('##METHODS_PART##'):
                        core_bridge.extend(methods_part)
                    elif line.startswith('##TIMESTAMP##'):
                        core_bridge.append('Generated on %s' % datetime.now())
                    else:
                        core_bridge.append(line.replace('\n',''))
        except IOError:
            print ("Can't open template file [%s]" % self.core_template)
            sys.exit(1) 

        #now we write to final file
        self.finalWrite(self.core_dest, core_bridge)

class DbusConstructor(Constructor):

    def __init__(self, bridge_template, options):
        Constructor.__init__(self, bridge_template, options)
        self.core_template="dbus_core_template.py" 
        self.frontend_template="dbus_frontend_template.py" 
        self.frontend_dest = self.core_dest="DBus.py" 

    def generateCoreSide(self):
        signals_part = []
        methods_part = []
        direct_calls = []
        sections = self.bridge_template.sections()
        sections.sort()
        for section in sections:
            function = self.getValues(section)
            print ("Adding %s %s" % (section, function["type"]))
            default = self.getDefault(section)
            arg_doc = self.getArgumentsDoc(section)
            async = "async" in self.getFlags(section)
            completion = {
        'sig_in':function['sig_in'] or '',
        'sig_out':function['sig_out'] or '',
        'category':'PLUGIN' if function['category'] == 'plugin' else 'CORE',
        'name':section, 
        'args':self.getArguments(function['sig_in'], name=arg_doc, default=default )
        }

            if function["type"] == "signal":
                completion['body'] = "pass" if not self.options.debug else 'debug ("%s")' % section
                signals_part.append("""\
    @dbus.service.signal(const_INT_PREFIX+const_%(category)s_SUFFIX,
                         signature='%(sig_in)s')
    def %(name)s(self, %(args)s):
        %(body)s
""" % completion)
                direct_calls.append("""\
    def %(name)s(self, %(args)s):
        self.dbus_bridge.%(name)s(%(args)s)
""" % completion)

            elif function["type"] == "method":
                completion['debug'] = "" if not self.options.debug else 'debug ("%s")\n%s' % (section,8*' ')
                completion['args_result'] = self.getArguments(function['sig_in'], name=arg_doc, unicode_protect=self.options.unicode)
                completion['async_comma'] = ', ' if async and function['sig_in'] else ''
                completion['async_args_def'] = 'callback=None, errback=None' if async else ''
                completion['async_args_call'] = 'callback=callback, errback=errback' if async else ''
                completion['async_callbacks'] = "('callback', 'errback')" if async else "None"
                methods_part.append("""\
    @dbus.service.method(const_INT_PREFIX+const_%(category)s_SUFFIX,
                         in_signature='%(sig_in)s', out_signature='%(sig_out)s',
                         async_callbacks=%(async_callbacks)s)
    def %(name)s(self, %(args)s%(async_comma)s%(async_args_def)s):
        %(debug)sreturn self._callback("%(name)s", %(args_result)s%(async_comma)s%(async_args_call)s)
""" % completion)

        #at this point, signals_part, methods_part and direct_calls should be filled,
        #we just have to place them in the right part of the template
        core_bridge = []
        const_override_pref = filter(lambda env: env.startswith(ENV_OVERRIDE), os.environ)
        const_override = [env[len(ENV_OVERRIDE):] for env in const_override_pref]
        try:
            with open(self.core_template) as core_template:
                for line in core_template:
                    if line.startswith('##SIGNALS_PART##'):
                        core_bridge.extend(signals_part)
                    elif line.startswith('##METHODS_PART##'):
                        core_bridge.extend(methods_part)
                    elif line.startswith('##DIRECT_CALLS##'):
                        core_bridge.extend(direct_calls)
                    else:
                        if line.startswith('const_'):
                            const_name = line[len('const_'):line.find(' = ')]
                            if const_name in const_override:
                                print ("const %s overriden" % const_name)
                                core_bridge.append('const_%s = %s' % (const_name, os.environ[ENV_OVERRIDE+const_name]))
                                continue
                        core_bridge.append(line.replace('\n',''))
        except IOError:
            print ("Can't open template file [%s]" % self.core_template)
            sys.exit(1) 

        #now we write to final file
        self.finalWrite(self.core_dest, core_bridge)

    def generateFrontendSide(self):
        methods_part = []
        sections = self.bridge_template.sections()
        sections.sort()
        for section in sections:
            function = self.getValues(section)
            print ("Adding %s %s" % (section, function["type"]))
            default = self.getDefault(section)
            arg_doc = self.getArgumentsDoc(section)
            async = "async" in self.getFlags(section)
            completion = {
        'sig_in':function['sig_in'] or '',
        'sig_out':function['sig_out'] or '',
        'category':'plugin' if function['category'] == 'plugin' else 'core',
        'name':section, 
        'args':self.getArguments(function['sig_in'], name=arg_doc, default=default)
        }

            if function["type"] == "method":
                completion['debug'] = "" if not self.options.debug else 'debug ("%s")\n%s' % (section,8*' ')
                completion['args_result'] = self.getArguments(function['sig_in'], name=arg_doc)
                completion['async_args'] = ', callback=None, errback=None' if async else ''
                completion['async_comma'] = ', ' if async and function['sig_in'] else ''
                completion['async_args_result'] = 'reply_handler=callback, error_handler=lambda err:errback(err._dbus_error_name[len(const_ERROR_PREFIX)+1:])' if async else ''
                result = "self.db_%(category)s_iface.%(name)s(%(args_result)s%(async_comma)s%(async_args_result)s)" % completion
                completion['result'] = ("unicode(%s)" if self.options.unicode and function['sig_out'] == 's' else "%s") % result
                methods_part.append("""\
    def %(name)s(self, %(args)s%(async_args)s):
        %(debug)sreturn %(result)s
""" % completion)

        #at this point, methods_part should be filled,
        #we just have to place it in the right part of the template
        frontend_bridge = []
        const_override_pref = filter(lambda env: env.startswith(ENV_OVERRIDE), os.environ)
        const_override = [env[len(ENV_OVERRIDE):] for env in const_override_pref]
        try:
            with open(self.frontend_template) as frontend_template:
                for line in frontend_template:
                    if line.startswith('##METHODS_PART##'):
                        frontend_bridge.extend(methods_part)
                    else:
                        if line.startswith('const_'):
                            const_name = line[len('const_'):line.find(' = ')]
                            if const_name in const_override:
                                print ("const %s overriden" % const_name)
                                frontend_bridge.append('const_%s = %s' % (const_name, os.environ[ENV_OVERRIDE+const_name]))
                                continue
                        frontend_bridge.append(line.replace('\n',''))
        except IOError:
            print ("Can't open template file [%s]" % self.frontend_template)
            sys.exit(1) 

        #now we write to final file
        self.finalWrite(self.frontend_dest, frontend_bridge)

class DbusXmlConstructor(Constructor):
    """Constructor for DBus XML syntaxt (used by Qt frontend)"""

    def __init__(self, bridge_template, options):
        Constructor.__init__(self, bridge_template, options)
        
        self.template="dbus_xml_template.xml" 
        self.core_dest="org.goffi.sat.xml"
        self.default_annotation = { 'a{ss}': 'StringDict',
                                    'a(sa{ss}as)': 'QList<Contact>',
                                    'a{i(ss)}': 'HistoryT',
                                    'a(sss)': 'QList<MenuT>',
                                    'a{sa{s(sia{ss})}}': 'PresenceStatusT',
                                    'a{sa{ss}}': 'ActionResultExtDataT',
                                  }

    def generateCoreSide(self):
        try:
            doc = minidom.parse(self.template)
            interface_elt = doc.getElementsByTagName('interface')[0]
        except IOError:
            print ("Can't access template")
            sys.exit(1)
        except IndexError:
            print ("Template error")
            sys.exit(1)

        sections = self.bridge_template.sections()
        sections.sort()
        for section in sections:
            function = self.getValues(section)
            print ("Adding %s %s" % (section, function["type"]))
            new_elt = doc.createElement('method' if function["type"]=='method' else 'signal')
            new_elt.setAttribute('name', section)
            args_in_str = self.getArguments(function['sig_in'])

            idx=0
            args_doc = self.getArgumentsDoc(section)
            for arg in self.argumentsParser(function['sig_in'] or ''):
                arg_elt = doc.createElement('arg')
                arg_elt.setAttribute('name', args_doc[idx][0] if args_doc.has_key(idx) else "arg_%i" % idx)
                arg_elt.setAttribute('type', arg)
                _direction = 'in' if function["type"]=='method' else 'out'
                arg_elt.setAttribute('direction', _direction)
                new_elt.appendChild(arg_elt)
                if "annotation" in self.options.flags:
                    if arg in self.default_annotation:
                        annot_elt = doc.createElement("annotation")
                        annot_elt.setAttribute('name', "com.trolltech.QtDBus.QtTypeName.In%d" % idx)
                        annot_elt.setAttribute('value', self.default_annotation[arg])
                        new_elt.appendChild(annot_elt)
                idx+=1
            
            if function['sig_out']:
                arg_elt = doc.createElement('arg')
                arg_elt.setAttribute('type', function['sig_out'])
                arg_elt.setAttribute('direction', 'out')
                new_elt.appendChild(arg_elt)
                if "annotation" in self.options.flags:
                    if function['sig_out'] in self.default_annotation:
                        annot_elt = doc.createElement("annotation")
                        annot_elt.setAttribute('name', "com.trolltech.QtDBus.QtTypeName.Out0")
                        annot_elt.setAttribute('value', self.default_annotation[function['sig_out']])
                        new_elt.appendChild(annot_elt)

            interface_elt.appendChild(new_elt)

        #now we write to final file
        self.finalWrite(self.core_dest, [doc.toprettyxml()])

class ConstructorError(Exception):
    pass

class ConstructorFactory:
    def create(self, bridge_template, options):
       if options.protocole=='dbus':
           return DbusConstructor(bridge_template, options)
       elif options.protocole=='mediawiki':
           return MediawikiConstructor(bridge_template, options)
       elif options.protocole=='dbus-xml':
           return DbusXmlConstructor(bridge_template, options)

       raise ConstructorError('Unknown constructor type')

class BridgeConstructor:
    def __init__(self):
        self.options = None
    
    def check_options(self):
        """Check command line options"""
        _usage="""
        %prog [options]

        %prog --help for options list
        """
        parser = OptionParser(usage=_usage,version=ABOUT % VERSION)

        parser.add_option("-p", "--protocole", action="store", type="string", default=DEFAULT_PROTOCOLE,
                    help="Generate bridge using PROTOCOLE (default: %s, possible values: [%s])" % (DEFAULT_PROTOCOLE, ", ".join(MANAGED_PROTOCOLES)))
        parser.add_option("-s", "--side", action="store", type="string", default="core",
                    help="Which side of the bridge do you want to make ? (default: %default, possible values: [core, frontend])")
        parser.add_option("-t", "--template", action="store", type="string", default='bridge_template.ini',
                    help="Use TEMPLATE to generate bridge (default: %default)")
        parser.add_option("-f", "--force", action="store_true", default=False,
                    help=("Force overwritting of existing files"))
        parser.add_option("-d", "--debug", action="store_true", default=False,
                    help=("Add debug information printing"))
        parser.add_option("--no_unicode", action="store_false", dest="unicode", default=True,
                    help=("Remove unicode type protection from string results"))
        parser.add_option("--flags", action="store", type="string", 
                    help=("Constructors' specific flags, comma separated"))


        (self.options, args) = parser.parse_args()
        self.options.flags = self.options.flags.split(',') if self.options.flags else []
        return args

    def go(self):
        self.check_options()
        self.template = Parser()
        try:
            self.template.readfp(open(self.options.template))
        except IOError:
            print ("The template file doesn't exist or is not accessible")
            exit(1)
        constructor = ConstructorFactory().create(self.template, self.options)
        if self.options.side == "core":
            constructor.generateCoreSide()
        elif self.options.side == "frontend":
            constructor.generateFrontendSide()

if __name__ == "__main__":
    bc = BridgeConstructor()
    bc.go()
