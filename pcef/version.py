#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# <Project>
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
Contains the PCEF version information
"""
#: PCEF major version
major = 0
#: PCEF minor version
minor = 1
#: PCEF build version (a new build is made when we upload a new package to pypi)
build = 0
#: PCEF version string
__version__ = "{0}.{1}.{2}-dev".format(major, minor, build)
