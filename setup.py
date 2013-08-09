#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# pyQode - Python/Qt Code Editor widget
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
This setup script packages the core package of pyQode: pyqode-core
"""
from setuptools import setup, find_packages


def read_version():
    with open("pyqode/core/__init__.py") as f:
        lines = f.read().splitlines()
        for l in lines:
            if "__version__" in l:
                return l.split("=")[1].strip()


def readme():
    return str(open('README.rst').read())


# get requirements
requirements = ['pygments']


setup(
    name='pyqode-core',
    namespace_packages=['pyqode'],
    version=read_version(),
    packages=find_packages(),
    keywords=["QCodeEditor", "PySide", "PyQt", "code editor"],
    package_data={'pyqode.core.ui': ['*.ui', 'rc/*']},
    package_dir={'pyqode': 'pyqode'},
    url='https://github.com/ColinDuquesnoy/pyQode-core',
    license='GNU LGPL v3',
    author='Colin Duquesnoy',
    author_email='colin.duquesnoy@gmail.com',
    description='Python/Qt Code Editor widget',
    long_description=readme(),
    install_requires=requirements,
    entry_points={'gui_scripts':
                  ['pyqode_designer = designer:main'],
                  'pyqode_plugins':
                  ['pyqode_core = pyqode.core.plugins.pyqode_core_plugin']},
    zip_safe=False
)
