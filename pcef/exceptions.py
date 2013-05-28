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
Contains all pcef exceptions
"""


class UnsupportedFeatureError(Exception):
    """
    This error is raised when a mode is not supported. This happens if you
    try to use a specific mode which requires a specific library to be installed
    (that is not part of the core requirements). Python modes are a good
    example of mode who might raise this exception (all python have a
    isSupported method that you can use when installing a mode).
    """
    pass
