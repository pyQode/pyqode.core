# -*- coding: utf-8 -*-
import os
import sys
from pyqode.core import widgets
from . import server


class GenericCodeEdit(widgets.GenericCodeEdit):
    """
    A generic code editor widget. This is just a CodeEdit with a preconfigured
    set of modes and panels.

    It does not have any language specific feature.
    """
    def __init__(self, parent):
        super(GenericCodeEdit, self).__init__(
            parent, server_script=os.path.join(os.getcwd(), 'server.exe')
            if hasattr(sys, "frozen") else server.__file__)

    def clone(self):
        clone = self.__class__(parent=self.parent())
        return clone
