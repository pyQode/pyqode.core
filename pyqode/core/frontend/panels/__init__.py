#!/usr/bin/env python
"""
This package contains the core panels
"""
from pyqode.core.frontend.panels.line_number import LineNumberPanel
from pyqode.core.frontend.panels.marker import MarkerPanel, Marker
from pyqode.core.frontend.panels.search_and_replace import \
    SearchAndReplacePanel

__all__ = ["LineNumberPanel", "SearchAndReplacePanel", "MarkerPanel",
           "Marker"]
