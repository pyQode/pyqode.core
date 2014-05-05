# -*- coding: utf-8 -*-
"""
This module contains the ErrorsTable designer plugin.
"""
from pyqode.core.frontend import widgets
from pyqode.core.designer_plugins import WidgetPlugin


class ErrorsTablePlugin(WidgetPlugin):
    """
    Designer plugin for TabWidget.
    """
    def klass(self):
        return widgets.ErrorsTable

    def objectName(self):
        return 'errorsTable'
