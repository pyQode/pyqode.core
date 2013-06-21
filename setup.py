#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# PCEF - Python/Qt Code Editing Framework
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
from setuptools import setup, find_packages
import sys

def read_version():
    with open("pcef/__init__.py") as f:
        lines = f.read().splitlines()
        for l in lines:
            if "__version__" in l:
                return l.split("=")[1].strip()

def readme():
    return str(open('README.rst').read())

# get requirements
requirements = ['pygments']
# use chardet 2 with python3
if sys.version_info[0] == 3:
    requirements += ["chardet2"]
else:
    requirements += ["chardet"]
# python editor requirements
if not '--no-python' in sys.argv:
    requirements += ['jedi', 'pep8', 'pyflakes']
    # todo check pylint with python3 on ubuntue, this does not works on win32
    # if sys.platform != "win32":
    #     requirements += ["pylint"]

setup(
    name='PCEF',
    version=read_version(),
    packages=find_packages(),
    keywords=["QCodeEditor", "PySide code editor"],
    package_data={'pcef.ui': ['rc/*']},
    package_dir={'pcef': 'pcef'},
    url='https://github.com/ColinDuquesnoy/PCEF',
    license='GNU LGPL v3',
    author='Colin Duquesnoy',
    author_email='colin.duquesnoy@gmail.com',
    description='Python Qt Code Editing Framework (P.C.E.F.)',
    long_description=readme(),
    install_requires=requirements,
    entry_points={'gui_scripts':
                  ['pcef_designer = designer:main',]},
    zip_safe=False
)
