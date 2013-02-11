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
PCEF is code editor framework for PySide applications

This is the setup script, install it as any python package.

.. note:: You will need to install PySide on your own
"""
from IPython.core.release import long_description
from setuptools import setup, find_packages
execfile('pcef/version.py')

with open('README.rst', 'r') as readme:
    long_desc = readme.read()


setup(
    name='PCEF',
    version=__version__,
    packages=find_packages(),
    package_data={'pcef.ui': ['rc/*'], 'examples.ui': ['rc/*']},
    package_dir={'pcef': 'pcef'},
    url='https://launchpad.net/qce/',
    license='GNU LGPL v3',
    author='Colin Duquesnoy',
    author_email='colin.duquesnoy@gmail.com',
    description='PySide Code Editing Framework (P.C.E.F.)',
    long_description=long_desc,
    requires=['pygments', 'PySide', 'jedi'],
    entry_points={'gui_scripts': ['pcef_generic_example = examples.generic_example:main']}
)
