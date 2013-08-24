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
This package contains the core panels (language independant)
"""
from pyqode.core.panels.folding import FoldingPanel
from pyqode.core.panels.line_number import LineNumberPanel
from pyqode.core.panels.marker import MarkerPanel, Marker
from pyqode.core.panels.search_and_replace import SearchAndReplacePanel

__all__ = ["LineNumberPanel", "SearchAndReplacePanel", "MarkerPanel",
           "Marker", "FoldingPanel"]
