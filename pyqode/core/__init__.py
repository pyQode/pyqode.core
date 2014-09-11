# -*- coding: utf-8 -*-
"""
The core package contains the core components for writing a pyqode based
application. It is the "de facto" requirement for any pyqode extension.

It contains the base classes for both the backend and the frontend and provides
a series of modes and panels that might be useful for any kind of code editor
widget, i.e. pyqode.core is a generic code editor widget.

pyQode is a client-server API. The client side API is called frontend while the
server side API is called backend.

pyqode is made up of the following top level packages/modules:
    - api
    - backend
    - dialogs
    - managers
    - modes
    - panels
    - qt: DEPRECATED (use pyqode.qt instead)
    - styles
    - widgets

"""

__version__ = '2.2.0'
