#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# PCEF - PySide Code Editing framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
PCEF is a framework to help creating a code editor in a pyside application.
This is the setup script, install it as any python package.
You will need to install PySide on your own.
"""
from setuptools import setup, find_packages

setup(
    name='PCEF',
    version='0.1.0-dev',
    packages=find_packages(),
    package_data={'pcef.ui': ['rc/*']},
    package_dir={'pcef': 'pcef'},
    url='https://launchpad.net/qce/',
    license='GNU LGPL v3',
    author='Colin Duquesnoy',
    author_email='colin.duquesnoy@gmail.com',
    description='PySide Code Editing Framework (P.C.E.F.)',
    requires=['pygments', 'PySide']
)
