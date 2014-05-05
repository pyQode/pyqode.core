# -*- coding: utf-8 -*-
"""
This module contains the CodeEdit designer plugin.
"""
from pyqode.core import frontend
from pyqode.core.designer_plugins import WidgetPlugin


class CodeEditPlugin(WidgetPlugin):
    """
    Designer plugin for CodeEdit.
    """
    def klass(self):
        return frontend.CodeEdit

    def objectName(self):
        return 'codeEdit'
