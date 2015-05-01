#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for pyqode.core
"""
from setuptools import setup, find_packages
from pyqode.core import __version__

#
# add ``build_ui command`` (optional, for development only)
# this command requires the following packages:
#   - pyqt-distutils
#   - pyqode-uic
#
import sys

try:
    from pyqt_distutils.build_ui import build_ui
    cmdclass = {'build_ui': build_ui}
except ImportError:
    cmdclass = {}


pygments_req = 'pygments'
if sys.version_info[0] == 3 and sys.version_info[1] == 2:
    # pygment 2 does not support Python 3.2
    pygments_req += "==1.6"


DESCRIPTION = 'PyQt/PySide Source Code Editor Widget'


def readme():
    if 'bdist_deb' in sys.argv or 'sdist_dsc' in sys.argv:
        return DESCRIPTION
    return str(open('README.rst').read())


setup(
    name='pyqode.core',
    namespace_packages=['pyqode'],
    version=__version__,
    packages=[p for p in find_packages() if 'test' not in p],
    keywords=["CodeEdit PyQt source code editor widget qt"],
    url='https://github.com/pyQode/pyqode.core',
    license='MIT',
    author='Colin Duquesnoy',
    author_email='colin.duquesnoy@gmail.com',
    description=DESCRIPTION,
    long_description=readme(),
    install_requires=[pygments_req, 'pyqode.qt', 'future'],
    entry_points={
        'console_scripts': [
            'pyqode-console = pyqode.core.tools.console:main'
        ],
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Widget Sets',
        'Topic :: Text Editors :: Integrated Development Environments (IDE)'])
