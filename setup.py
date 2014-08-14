#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for pyqode.core
"""
from setuptools import setup, find_packages

#
# add ``build_ui command`` (optional, for development only)
# this command requires the following packages:
#   - pyqt_distutils
#   - pyqode-uic
#
try:
    from pyqt_distutils.build_ui import build_ui
    cmdclass = {'build_ui': build_ui}
except ImportError:
    cmdclass = {}


def read_version():
    with open("pyqode/core/__init__.py") as f:
        lines = f.read().splitlines()
        for l in lines:
            if "__version__" in l:
                return l.split("=")[1].strip().replace("'", '')


def readme():
    return str(open('README.rst').read())


setup(
    name='pyqode.core',
    namespace_packages=['pyqode'],
    version=read_version(),
    packages=[p for p in find_packages() if 'test' not in p],
    keywords=["CodeEdit PyQt source code editor widget qt"],
    url='https://github.com/pyQode/pyqode.core',
    license='MIT',
    author='Colin Duquesnoy',
    author_email='colin.duquesnoy@gmail.com',
    description='Python/Qt Code Editor widget',
    long_description=readme(),
    install_requires=['pygments', 'pyqode.qt'],
    entry_points={
        'pyqode_plugins':
            ['code_edit = pyqode.core._designer_plugins'],
        'pygments.styles':
            ['qt = pyqode.core.styles.qt:QtStyle',
             'darcula = pyqode.core.styles.darcula:DarculaStyle']
    },
    zip_safe=False,
    cmdclass=cmdclass,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: Qt',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Widget Sets',
        'Topic :: Text Editors :: Integrated Development Environments (IDE)'])
