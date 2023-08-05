#!/usr/bin/env python
# -*- coding: latin-1 -*-
##
# Copyright 2009-2012 Ghent University
# Copyright 2009-2012 Stijn De Weirdt
# Copyright 2012 Andy Georges
#
# This file is part of VSC-tools,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/VSC-tools
#
# VSC-tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# VSC-tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with VSC-tools. If not, see <http://www.gnu.org/licenses/>.
##
"""
VSC-tools distribution setup.py

Usage:
------
python setup.py [<targetname>] <usual distutils commands and options>

targetname can be:
    vsc-all : build all (default if no target is specified)
    vsc-allinone : build all as single target (ie 1 tarball/spec/rpm)
    vsc-showall : just show all possible targets


    vsc-tools ## this is the name of the allinone target
    vsc-base
    vsc-mympirun
    ...

Warning:
--------
To utilise the fake mpirun wrapper,
 - mympirun must be installed in path that resembles SOME_PREFIX/mympirun.*?/bin/
 - the fake path SOME_PREFIX/mympirun.*?/bin/fake must be added to the PATH variable
     so it is found before the real mpirun
 - this should be fine when installing with --prefix or --user

Example usage:
--------------
build all and install in user space (~/.local/lib/python2.X/site-packages)
    python setup.py build -b /tmp/vsc$USER install --user

build under /tmp/vsc, install with prefix /tmp/vsc/testinstall
(scripts in PREFIX/bin; python modules under PREFIX/lib/python2.X/site-packages)
    python setup.py vsc-mympirun clean build -b /tmp/vsc install --prefix /tmp/vsc/testinstall

make rpm for all targets at once (works for single target)
    python setup.py clean sdist -d /tmp/vsc$USER bdist_rpm --bdist-base /tmp/vsc$USER -d /tmp/vsc$USER clean ; rm -f MANIFEST

easy_install
------------
## 1st run: without dependencies
easy_install --user -N http://github.com/hpcugent/VSC-tools/tarball/master

## 2nd run with dependencies to resolve external ones
easy_install --user http://github.com/hpcugent/VSC-tools/tarball/master


TODO:
    create http://hpcugent.github.com/VSC-tools page, short description per package ?

Tip from docs:
    On the other hand, this doesn't help the developer to find the cause of the failure.
    For this purpose, the DISTUTILS_DEBUG environment variable can be set to anything except
    an empty string, and distutils will now print detailed information what it is doing, and
    prints the full traceback in case an exception occurs.

"""
import shutil
import os, os.path
import sys
from distutils import log  # also for setuptools
from distutils.dir_util import remove_tree

## generate these somehow from lib/vsc/mympirun/mpi/mpi.py
FAKE_SUBDIRECTORY_NAME = 'fake'
MYMPIRUN_ALIASES = ['%smpirun' % x for x in ['i', 'ih', 'o', 'm', 'mh', 'mm', 'q', 'm2', 'm2h']] + ['myscoop']
ENVNAME = 'VSC_TOOLS_SETUP_TARGET'

## 0 : WARN (default), 1 : INFO, 2 : DEBUG
log.set_verbosity(1)


try:
    ## setuptools makes copies of the scripts, does not preserve symlinks
    #raise("no setuptools")  # to try distutils, uncomment
    from setuptools import setup
    from setuptools.command.install_scripts import install_scripts
    from setuptools.command.easy_install import easy_install

    ## uch uch, easy_install ignores the easy_install cmdclass
    _orig_install_egg_scripts = sys.modules['setuptools.command.easy_install'].easy_install.install_egg_scripts

    def _new_install_egg_scripts(self, dist):
        orig_func = dist.metadata_listdir
        def new_func(txt):
            """The original metadata_listdir assumes no subdirectories in scripts dir.
                fake/mpirun is the exception (mpirun itself is not listed !)
                    The function is used through a whole bunch of Egg classes, now way we can easily intercept this
            """
            res = orig_func(txt)
            if txt == 'scripts':
                if FAKE_SUBDIRECTORY_NAME in res:
                    idx = res.index(FAKE_SUBDIRECTORY_NAME)
                    if idx >= 0:
                        res[idx] = '%s/mpirun' % FAKE_SUBDIRECTORY_NAME
            return res
        dist.metadata_listdir = new_func
        _orig_install_egg_scripts(self, dist)

    sys.modules['setuptools.command.easy_install'].easy_install.install_egg_scripts = _new_install_egg_scripts

except:
    from distutils.core import setup
    from distutils.command.install_scripts import install_scripts


class vsc_install_scripts(install_scripts):
    """Create the (fake) links for mympirun
        also remove .sh and .py extensions from the scripts
    """
    def __init__(self, *args):
        install_scripts.__init__(self, *args)
        self.original_outfiles = None

    def run(self):
        # old-style class
        install_scripts.run(self)

        self.original_outfiles = self.get_outputs()[:]  # make a copy
        self.outfiles = []  # reset it
        for script in self.original_outfiles:
            # remove suffixes for .py and .sh
            if script.endswith(".py") or script.endswith(".sh"):
                shutil.move(script, script[:-3])
                script = script[:-3]
            self.outfiles.append(script)

            if script.endswith('/mympirun'):
                # make the fake dir, create all symlinks

                # make all links
                # they are create with relative paths !

                rel_script = os.path.basename(script)
                rel_script_dir = os.path.dirname(script)

                # abspath: all_syms = [os.path.join(self.install_dir, x) for x in MYMPIRUN_ALIASES]
                # abspath: all_syms.append(os.path.join(abs_fakepath, 'mpirun'))
                # with relative paths, we also ne to chdir for the fake/mpirun and ref to ../mympirun
                previous_pwd = os.getcwd()

                os.chdir(rel_script_dir)
                for sym_name in MYMPIRUN_ALIASES:
                    if os.path.exists(sym_name):
                        os.remove(sym_name)
                    os.symlink(rel_script, sym_name)
                    newoutfile = os.path.join(rel_script_dir, sym_name)
                    self.outfiles.append(newoutfile)
                    log.info("symlink %s to %s newoutfile %s" % (rel_script, sym_name, newoutfile))

                # fake mpirun
                os.chdir(previous_pwd)
                abs_fakepath = os.path.join(self.install_dir, FAKE_SUBDIRECTORY_NAME)
                if not os.path.isdir(abs_fakepath):
                    log.info("creating abs_fakepath %s" % abs_fakepath)
                    os.mkdir(abs_fakepath)
                else:
                    log.info("not creating abs_fakepath %s (already exists)" % abs_fakepath)

                os.chdir(abs_fakepath)  # abs_fakepath si not always absolute
                fake_mpirun = os.path.join(abs_fakepath, 'mpirun')
                if os.path.exists(fake_mpirun):
                    os.remove(fake_mpirun)

                mympirun_src = '../%s' % rel_script
                os.symlink(mympirun_src, 'mpirun')
                self.outfiles.append(fake_mpirun)
                log.info("symlink %s to %s newoutfile %s" % (mympirun_src, 'mpirun', fake_mpirun))

                os.chdir(previous_pwd)


## authors
sdw = ('Stijn De Weirdt', 'stijn.deweirdt@ugent.be')
jt = ('Jens Timmermans', 'jens.timmermans@ugent.be')
kh = ('Kenneth Hoste', 'kenneth.hoste@ugent.be')
ag = ('Andy Georges', 'andy.georges@ugent.be')
wdp = ('Wouter Depypere', 'wouter.depypere@ugent.be')
lm = ('Luis Fernando Munoz Meji­as', 'luis.munoz@ugent.be')

## shared target config
SHARED_TARGET = {'url':'http://hpcugent.github.com/VSC-tools',
                 'download_url':'https://github.com/hpcugent/VSC-tools',
                 'package_dir' : {'': 'lib'},
                 'cmdclass' : {"install_scripts": vsc_install_scripts,
                               },
                 }

## meta-package for allinone target
VSC_ALLINONE = {'name': 'vsc-tools',
                'version': '0.9',
                }

## specific info
VSC_BASE = {'name' : 'vsc-base',
            'version': "0.9" ,
            'author': [sdw, jt],
            'maintainer': [sdw, jt],
            'install_requires': ['paycheck>=1.0.2'],
            'packages': ['vsc', 'vsc.utils'],
            'scripts': ['bin/logdaemon.py', 'bin/startlogdaemon.sh']
            }


VSC_LDAP = {'name': 'vsc-ldap',
            'version': '0.9',
            'author': [ag, sdw, wdp],
            'maintainer': [ag],
            'packages': ['vsc/ldap'],
            'namespace_packages': ['vsc', 'vsc.ldap'],
            'py_modules': [
                'vsc.__init__',
                'vsc.ldap.filter',
                'vsc.ldap.group',
                'vsc.ldap.ldap_utils',
                'vsc.ldap.project',
                'vsc.ldap.utils',
                'vsc.ldap.user',
                'vsc.ldap.vo',
                ],
            'scripts': []
            }

VSC_MYMPIRUN = {'name':'vsc-mympirun',
                'version':'3.0.0',
                'author':[sdw],
                'maintainer':[sdw],
                'install_requires':['vsc-base>=0.9.0'],
                'packages':['vsc.mympirun', 'vsc.mympirun.mpi', 'vsc.mympirun.rm'],
                'py_modules': ['vsc.__init__'],
                'namespace_packages':['vsc'],
                'scripts':['bin/mympirun.py', 'bin/pbsssh.sh', 'bin/sshsleep.sh', 'bin/mympisanity.py'],
                }

VSC_MYMPIRUN_SCOOP = {'name':'vsc-mympirun-scoop',
                      'version':'3.0.0',
                      'author':[sdw],
                      'maintainer':[sdw],
                      'install_requires':['vsc-mympirun>=3.0.0', 'scoop>=0.5.4'],
                      'packages':['vsc.mympirun.scoop', 'vsc.mympirun.scoop.worker'],
                      'namespace_packages':['vsc', 'vsc.mympirun'],
                      'py_modules': ['vsc.__init__', 'vsc.mympirun.__init__'],
                      #'scripts':['bin/mympirun.py'], ## is installed with vsc-mympirun, including myscoop
                      }


###
### BUILDING
###

def parse_target(target):
    """Add some fields"""
    new_target = {}
    new_target.update(SHARED_TARGET)
    for k, v in target.items():
        if k in ('author', 'maintainer'):
            if not isinstance(v, list):
                log.error("%s of config %s needs to be a list (not tuple or string)" % (k, target['name']))
                sys.exit(1)
            new_target[k] = ";".join([x[0] for x in v])
            new_target["%s_email" % k] = ";".join([x[1] for x in v])
        else:
            new_target[k] = type(v)()
            new_target[k] += v
    log.info("parse_target: new_target %s" % new_target)
    return new_target



def make_all_targets():
    all_targets = [VSC_BASE, VSC_LDAP, VSC_MYMPIRUN, VSC_MYMPIRUN_SCOOP, VSC_ALLINONE]
    #all_targets = [VSC_BASE, VSC_ALLINONE]
    registered_names = ['vsc-all', 'vsc-allinone'] + [x['name'] for x in all_targets]

    tobuild = os.environ.get(ENVNAME, 'vsc-all')  ## default all
    log.debug('main: going to build %s (set through env: %s)' % (tobuild, ENVNAME in os.environ))
    if sys.argv[1] == 'vsc-showall':
        log.error("Valid targets: %s" % " ".join(registered_names))
        sys.exit(0)
    elif sys.argv[1] in registered_names:
        tobuild = sys.argv[1]
        sys.argv.pop(1)

    ## create allinone / vsc-tools target
    for target in all_targets:
        for k, v in target.items():
            if k in ('name', 'version',):
                continue
            if not k in VSC_ALLINONE:
                VSC_ALLINONE[k] = type(v)()

            if isinstance(v, (list, str)):
                VSC_ALLINONE[k] += v
            else:
                log.error('unsupported type cfgname %s key %s value %s' % (target['name'], k, v))
                sys.exit(1)

    ## sanitize allinone/vsc-tools
    for k, v in VSC_ALLINONE.items():
        if isinstance(v, list):
            VSC_ALLINONE[k] = list(set(VSC_ALLINONE[k]))
            VSC_ALLINONE[k].sort()

    if tobuild == 'vsc-allinone':
        ## reset all_targets
        all_targets = [VSC_ALLINONE]

    ## build what ?
    return tobuild, all_targets


def cleanup():
    try:
        remove_tree('build')
    except OSError, _:
        pass


def action_target(tobuild, target):
    target_name = target['name']
    if (tobuild is not None) and not (tobuild in ('vsc-all', 'vsc-allinone' , target_name,)):
        return
    if tobuild == 'vsc-all' and target_name == 'vsc-tools':
        ## vsc-tools / allinone is not a default when vsc-all is selected
        return

    ## froim now on, build the exact targets.
    os.environ[ENVNAME] = target_name
    os.putenv(ENVNAME, target_name)
    x = parse_target(target)

    cleanup()

    setup(**x)

    cleanup()

if __name__ == '__main__':

    _tobuild, _all_targets = make_all_targets()


    for _target in _all_targets:
        action_target(_tobuild, _target)

