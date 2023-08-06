#!/usr/bin/env python
# -*- coding: utf-8 -*-#
# @(#)setup.py
#
#
# Copyright (C) 2013, GC3, University of Zurich. All rights reserved.
#
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

__docformat__ = 'reStructuredText'

import os
import sys
import shutil

from setuptools.command import sdist
del sdist.finders[:]

ANSIBLE_PB_DIR = 'elasticluster/providers/ansible-playbooks'

def ansible_pb_files():
    basedir = os.path.dirname(__file__)
    ansible_data = [('share/elasticluster/etc', ['docs/config.template.ini'])]
    for (dirname, dirnames, filenames) in os.walk(ANSIBLE_PB_DIR):
        tmp = []
        for fname in filenames:
            if fname.startswith('.git'): continue
            tmp.append(os.path.join(dirname, fname))
        ansible_data.append((os.path.join('share', dirname), tmp))
    return ansible_data

from setuptools import setup, find_packages
setup(
    name = "elasticluster",
    version = "0.1",
    packages = find_packages(),
    install_requires = [
        'boto',
        'PyCLI',
        'paramiko',
        'ansible',  # works from pip, does not work from setup.py
        ],
    data_files = ansible_pb_files(),
    entry_points = {
        'console_scripts': [
            'elasticluster = elasticluster.main:main',
            ]
        },
    )

if __name__ == "__main__":
    if sys.argv[1] in ['develop', 'install']:
        develop = True if sys.argv[1] == 'develop' else False
        curdir = os.path.abspath(os.path.dirname(__file__))
        sharedir = os.path.join(os.path.abspath(sys.prefix), 'share', 'elasticluster')
        etcdir = os.path.join(sharedir, 'etc')
        templatecfg = os.path.join(curdir, 'docs', 'config.template.ini')
        templatedest = os.path.join(etcdir, os.path.basename(templatecfg))
        ansibledest = os.path.join(sharedir, 'providers', 'ansible-playbooks')
        ansiblesrc = os.path.join(curdir, 'elasticluster', 'providers', 'ansible-playbooks')

        if not os.path.exists(sharedir):
            os.makedirs(sharedir)
            
        if not os.path.exists(etcdir):
            os.makedirs(etcdir)

        if not os.path.exists(os.path.dirname(ansibledest)):
            os.makedirs(os.path.dirname(ansibledest))

        if not os.path.exists(ansibledest):
            if develop:
                os.symlink(ansiblesrc, ansibledest)
            else:
                shutil.copytree(ansiblesrc, ansibledest)

        if not os.path.exists(templatedest):
            if develop:
                os.symlink(templatecfg, templatedest)
            else:
                shutil.copy(templatecfg, etcdir)
