Source Code Editor widget for PyQt4
===================================

Status
------

Package:
++++++++


.. image:: http://img.shields.io/pypi/v/pyqode.core.png
    :target: https://pypi.python.org/pypi/pyqode.core/
    :alt: Latest PyPI version

.. image:: http://img.shields.io/pypi/dm/pyqode.core.png
    :target: https://pypi.python.org/pypi/pyqode.core/
    :alt: Number of PyPI downloads


Stable (master):
++++++++++++++++

.. image:: https://travis-ci.org/pyQode/pyqode.core.svg?branch=master
    :target: https://travis-ci.org/pyQode/pyqode.core
    :alt: Travis-CI build status

.. image:: https://coveralls.io/repos/pyQode/pyqode.core/badge.png?branch=master
    :target: https://coveralls.io/r/pyQode/pyqode.core?branch=develop
    :alt: Coverage Status


Unstable (develop):
+++++++++++++++++++

.. image:: https://travis-ci.org/pyQode/pyqode.core.svg?branch=develop
    :target: https://travis-ci.org/pyQode/pyqode.core
    :alt: Travis-CI build status

.. image:: https://coveralls.io/repos/pyQode/pyqode.core/badge.png?branch=develop
    :target: https://coveralls.io/r/pyQode/pyqode.core?branch=develop
    :alt: Coverage Status

.. image:: https://badge.waffle.io/pyqode/pyqode.core.png?label=status:ready&title=Ready 
    :target: https://waffle.io/pyqode/pyqode.core
    :alt: 'Tasks ready to be implemented'
    
.. image:: https://badge.waffle.io/pyqode/pyqode.core.png?label=status:in progress&title=In progress
    :target: https://waffle.io/pyqode/pyqode.core
    :alt: 'Tasks in progress'

.. image:: https://badge.waffle.io/pyqode/pyqode.core.png?label=status:done&title=Done
    :target: https://waffle.io/pyqode/pyqode.core
    :alt: 'Tasks done in develop branch'


About pyQode
------------

pyQode is a *flexible source code editor widget* forPyQt4 applications.

**pyQode is a library/widget, not an IDE**. *You can see it as an alternative to QScintilla.*


pyQode is a **namespace package** made up of the following official packages:

  - `pyqode.core`_: core package

  - `pyqode.python`_: python support (code completion, ...)

  - `pyqode.designer`_: Starts Qt designer with all pyqode plugins

.. _pyqode.core: https://github.com/pyQode/pyqode.core
.. _pyqode.python: https://github.com/pyQode/pyqode.python
.. _pyqode.designer: https://github.com/pyQode/pyqode.designer

**pyqode.core** is the foundation package, it contains the pyqode base classes
(CodeEdit, Mode, Panel) and a set of builtin modes and panels that are useful
for any kind of code editor. With pyqode.core you can already create a generic
code editor (similar to gedit, notepad++) with only a few lines of code.

Features
--------

Here are the core features:

-  simple widget based on QPlainTextEdit
-  easily customisable (modes and panels)
-  native look and feel close to Qt creator
-  builtin modes and panels (folding, line number, code completion,
   syntax highlighting)
-  Qt Designer plugin
- client/server architecture for smooth, non-blocking UI.


License
-------

pyQode is licensed under the MIT license.


Requirements
------------

pyqode.core depends on the following libraries:

-  Python 3 (>= 3.2)
-  PyQt4
-  pygments


Installation
------------
You need to install PyQt4 by yourself.

Then you can install pyqode.core using pip (for python3)::

    $ pip3 install pyqode.core

Testing
-------

pyqode.core now have a test suite and measure its coverage.

To run the test and see the coverage report run the following command (you don't need
to install anything)::

    $ python3 runtests.py

Resources
---------

- `Downloads`_
- `Source repository`_
- `Documentation`_
- `Wiki`_

.. _Downloads: https://github.com/pyQode/pyqode.core/releases
.. _Source repository: https://github.com/pyQode/pyqode.core/
.. _Documentation: http://pyqodecore.readthedocs.org/en/latest/
.. _Wiki: https://github.com/pyQode/pyqode.core/wiki

Snapshots
---------

Here are a few snapshots of the notepad example application (snapshots
taken on a Gnome 3 desktop):

.. image:: doc/source/_static/notepad.png
    :alt: Default style

.. image:: doc/source/_static/notepad-monokai.png
    :alt: Monokai style
