#!/usr/bin/env python
"""
This package contains the core panels
"""
from pyqode.core.panels.line_number import LineNumberPanel
from pyqode.core.panels.marker import MarkerPanel, Marker
from pyqode.core.panels.search_and_replace import SearchAndReplacePanel

__all__ = ["LineNumberPanel", "SearchAndReplacePanel", "MarkerPanel",
           "Marker"]
