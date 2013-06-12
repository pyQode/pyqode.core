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

# properly get pcef version
# execfile('pcef/__init__.py')
__version__ = "1.0.0-dev"

# get long description
with open('README.rst', 'r') as readme:
    long_desc = readme.read()


long_desc = """
PySide Code Editing Framework
=====================================

PCEF is code editing framework for PySide applications.

It provides a flexible code editor ready to use in any PySide
applications. Flexibility is achieved through a system of editor extensions
(custom panels and modes).

In addition to the base widget, some preconfigured editors are available
(a generic code editor and a python editor).

Here are the core features:

* **flexible framework** to add custom panels/modes
* **syntax highlighting mode** (using pygments)
* **code completion**
* line number Panel
* **code folding** Panel
* markers Panel (to add breakpoints, bookmarks, errors,...)
* right margin indicator mode
* active line highlighting mode
* **editor zoom** mode
* find and replace Panel
* **text decorations** (squiggle, box)
* **easy styling** (built-in white and dark styles + possibility to customize
  using **JSON style schemes**)
* auto indent mode(indentation level is based on the previous line indent)

Here are the python specific features:

* code completion (using Jedi)
* calltips
* syntax and style checking (using pylint, pyflakes and pep8)
* code folder
* smart indent
"""


setup(
    name='PCEF',
    version=__version__,
    packages=find_packages(),
    keywords=["QCodeEditor", "PySide code editor"],
    package_data={'pcef.ui': ['rc/*'], 'examples.ui': ['rc/*']},
    package_dir={'pcef': 'pcef'},
    url='https://github.com/ColinDuquesnoy/PCEF',
    license='GNU LGPL v3',
    author='Colin Duquesnoy',
    author_email='colin.duquesnoy@gmail.com',
    description='PySide Code Editing Framework (P.C.E.F.)',
    long_description=long_desc,
    # install_requires=['pygments', 'jedi', 'pep8', 'qdarkstyle', 'pylint',
    #                   'pyflakes'],
    entry_points={'gui_scripts':
                  ['pcef_generic_example = examples.generic_example:main',
                   'pcef_python_example = examples.python_example:main']},
)
