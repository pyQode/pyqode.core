# -*- coding: utf-8 -*-
"""
The core package contains the core components for writing a pyqode based
application. It is the "de facto" requirement for any pyqode extension.

It contains the base classes for both the backend and the frontend and provides
a series of modes and panels that might be useful for any kind of code editor
widget, i.e. pyqode.core is a generic code editor widget.

pyQode is a client-server API. The client side API is called frontend while the
server side API is called backend.

Frontend is implemented in python3 but the backend must supports both python2
and python3 in order to be able to run with any python interpreter
(this is needed to run tools such as pep8 and jedi on the backend and still
support python2 syntax).

pyqode is made up of the following top level packages/modules:

    - frontend: any class/function used to implement the client
                side GUI application
    - backend: any class/function used to implement the server side application

"""

__version__ = '2.0.0-beta2'
