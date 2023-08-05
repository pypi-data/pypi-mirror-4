#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SAT: a jabber client
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

from distribute_setup import use_setuptools
use_setuptools()
from setuptools.command.install import install
from setuptools import setup
from distutils.file_util import copy_file
import os,sys,subprocess
from stat import ST_MODE

NAME = 'sat'
LAUNCH_DAEMON_COMMAND = 'sat'

class MercurialException(Exception):
    pass

def module_installed(module_name):
    """Try to import module_name, and return False if it failed
    @param module_name: name of the module to test
    @return: True if successful"""
    try:
        __import__(module_name)
    except:
        return False
    return True

class custom_install(install):
    
    def custom_auto_options(self):
        """Change options for twistd in the shell script
        Mainly change the paths"""
        sh_buffer = ""
        run_dir = os.path.dirname(self.sh_script_path)
        with open(self.sh_script_path,'r') as sh_file:
            for ori_line in sh_file:
                if ori_line.startswith('DAEMON='):
                    dest_line = 'DAEMON=""\n' #we want to launch sat as a daemon
                elif ori_line.startswith('TAP_PATH='):
                    dest_line = 'TAP_PATH="%s/"\n' % run_dir
                elif ori_line.startswith('PYTHON='):
                    dest_line = 'PYTHON="%s"\n' % sys.executable
                else:
                    dest_line = ori_line
                sh_buffer += dest_line
        
        with open(self.sh_script_path,'w') as sh_file:
            sh_file.write(sh_buffer)

    
    def custom_create_links(self):
        """Create symbolic links to executables"""
        #the script which launch the daemon
        links = [(self.sh_script_path,LAUNCH_DAEMON_COMMAND),]
        for source,dest in links:
            dest_name, copied = copy_file(source, os.path.join(self.install_scripts, dest), link='sym')
            assert (copied)
            #we change the perm in the same way as in the original install_scripts
            mode = ((os.stat(dest_name)[ST_MODE]) | 0555) & 07777
            os.chmod(dest_name, mode)

    def run(self):
        install.run(self)
        sys.stdout.write ('running post installation stuff\n')
        sys.stdout.flush()
        self.sh_script_path = os.path.join(self.install_lib,'sat','sat.sh')
        self.primitivus_path = os.path.join(self.install_lib,'sat_frontends','primitivus')
        self.custom_auto_options()
        self.custom_create_links()


def preinstall_check():
    """Check presence of problematic dependencies, and try to install them with package manager
    This ugly stuff is necessary as distributions are not installed correctly with setuptools/distribute
    Hope to remove this at some point"""

    #modules_tocheck=['twisted', 'twisted.words', 'twisted.web', 'wx', 'urwid']
    modules_tocheck=['wx','gobject'] #XXX: wx is the only one to be really difficult to install, python-gobject is not up-to-date in PyPi

    package = {'twisted':'python-twisted-core',
               'twisted.words':'python-twisted-words',
               'twisted.web':'python-twisted-web',
               'wx':'python-wxgtk2.8',
               'urwid':'python-urwid',
               'gobject':'python-gobject',
               'mercurial':'mercurial'} #this dict map dependencies to packages names for debian distributions

    sys.stdout.write ("Running pre-installation dependencies check\n")
    
    #which modules are not installed ?
    modules_toinstall = filter(lambda mod:not module_installed(mod),modules_tocheck)
    """#is mercurial available ?
    hg_installed = subprocess.call('which hg', stdout=open('/dev/null', 'w'), shell=True) == 0
    if not hg_installed:
        modules_toinstall.append('mercurial')""" #hg can be installed from pypi
    
    if modules_toinstall:
        #are we on a distribution using apt ?
        apt_path = subprocess.Popen('which apt-get', stdout=subprocess.PIPE, shell=True).communicate()[0][:-1]
        not_installed=set()
        if apt_path:
            #we have apt, we'll try to use it
            for module_name in modules_toinstall:
                package_name = package[module_name]
                sys.stdout.write ("Installing %s\n" % package_name)
                success = subprocess.call('%s -qy install %s' % (apt_path,package_name), shell=True) == 0
                if not success:
                    not_installed.add(module_name)
        else:
            not_installed=set(modules_toinstall)

        if not_installed:
            #some packages can't be automatically installed, we print their name for manual installation
            sys.stdout.write ("You should install the following dependencies with your distribution recommanded tool before installing %s:\n" % NAME)
            for module_name in not_installed:
                sys.stdout.write ("- %s (Debian name: %s)\n" % (module_name,package[module_name]))
            sys.exit(2)
            

if sys.argv[1].lower() in ['egg_info','install']:
    #we only check dependencies if egg_info or install is used
    install_opt = os.environ.get("SAT_INSTALL","")
    if not "nopreinstall" in install_opt: #user can force preinstall skipping 
        preinstall_check()

setup(name=NAME,
      version='0.3.0',
      description=u'Salut à Toi multi-frontend XMPP client',
      long_description=u'Salut à Toi (SàT) is a XMPP client based on a daemon/frontend architecture. Its multi-frontends (desktop, web, console interface, CLI, etc) and multi-purposes (instant messaging, microblogging, games, file sharing, etc).',
      author='Goffi (Jérôme Poisson)',
      author_email='goffi@goffi.org',
      url='http://sat.goffi.org',
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'Environment :: X11 Applications :: GTK',
                   'Framework :: Twisted',
                   'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
                   'Operating System :: POSIX :: Linux',
                   'Topic :: Communications :: Chat'],
      package_dir = {'sat':'src', 'sat_frontends':'frontends/src'},
      packages=['sat','sat.tools','sat.bridge', 'sat.plugins', 'sat.test', 'sat.core', 'sat.memory',
                'sat_frontends', 'sat_frontends.bridge', 'sat_frontends.quick_frontend',
                'sat_frontends.primitivus', 'sat_frontends.wix'],
      package_data = {'sat': ['sat.tac','sat.sh'],
                      'sat_frontends': ['wix/COPYING']},
      data_files=[(os.path.join(sys.prefix,'share/locale/fr/LC_MESSAGES'), ['i18n/fr/LC_MESSAGES/sat.mo']),
                  (os.path.join(sys.prefix,'share/locale/fr/LC_MESSAGES'), ['frontends/i18n/fr/LC_MESSAGES/sat_frontend.mo']),
                  (os.path.join(sys.prefix,'share/locale/fr/LC_MESSAGES'), ['frontends/src/jp/i18n/fr/LC_MESSAGES/jp.mo']),
                  ('share/doc/%s' % NAME, ['CHANGELOG', 'COPYING', 'INSTALL', 'README', 'README4TRANSLATORS']),
                  ],
      scripts=['frontends/src/jp/jp', 'frontends/src/primitivus/primitivus', 'frontends/src/wix/wix'],
      zip_safe=False,
      dependency_links = ['http://www.blarg.net/%7Esteveha/pyfeed-0.7.4.tar.gz','http://www.blarg.net/%7Esteveha/xe-0.7.4.tar.gz'],
      install_requires=['twisted', 'wokkel', 'progressbar', 'urwid', 'urwid-satext','pyfeed','xe', 'mutagen'],
      cmdclass=dict(install=custom_install),
      ) #XXX: wxpython doesn't work, it's managed with preinstall_check

