#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 Colin Duquesnoy
#
# This file is part of pyQode.
#
# pyQode is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# pyQode is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with pyQode. If not, see http://www.gnu.org/licenses/.
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
                return l.split("=")[1].strip().replace('"', '')

print(read_version())

def readme():
    return str(open('README.rst').read())


# get requirements
requirements = ['pygments']

packages = find_packages()
setup(
    name='pyqode.core',
    namespace_packages=['pyqode'],
    version=read_version(),
    packages=packages,
    keywords=["QCodeEditor", "PySide", "PyQt", "code editor"],
    package_data={'pyqode.core.ui': ['*.ui', '*.qrc', 'rc/*']},
    #package_dir={'pyqode': 'pyqode', "pyqode_designer":},
    url='https://github.com/ColinDuquesnoy/pyQode-core',
    license='GNU LGPL v3',
    author='Colin Duquesnoy',
    author_email='colin.duquesnoy@gmail.com',
    description='Python/Qt Code Editor widget',
    long_description=readme(),
    install_requires=requirements,
    entry_points={'gui_scripts':
                  ['pyqode_designer = pyqode_designer.designer:main'],
                  'pyqode_plugins':
                  ['pyqode_core = pyqode.core.plugins.pyqode_core_plugin']},
    zip_safe=False
)
