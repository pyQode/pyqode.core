.. image:: https://raw.githubusercontent.com/pyQode/pyqode.core/develop/doc/source/_static/pyqode-banner.png


About
-----

.. image:: http://img.shields.io/pypi/v/pyqode.core.png
   :target: https://pypi.python.org/pypi/pyqode.core/
   :alt: Latest PyPI version

.. image:: http://img.shields.io/pypi/dm/pyqode.core.png
   :target: https://pypi.python.org/pypi/pyqode.core/
   :alt: Number of PyPI downloads

.. image:: https://travis-ci.org/pyQode/pyqode.core.svg?branch=master   
   :target: https://travis-ci.org/pyQode/pyqode.core                      
   :alt: Travis-CI build status                                                                                                       

.. image:: https://coveralls.io/repos/pyQode/pyqode.core/badge.png?branch=master     
   :target: https://coveralls.io/r/pyQode/pyqode.core?branch=master       
   :alt: Coverage Status


pyQode is a *flexible source code editor widget* for PyQt/PySide applications.

**pyQode is a library/widget, not an IDE**. *You can see it as an alternative
to QScintilla.*

pyQode is organised as a **namespace package** made up of the following
official packages:

- `pyqode.core`_: core package
- `pyqode.python`_: python support (code completion, ...)
- `pyqode.designer`_: Starts Qt designer with all pyqode plugins

**pyqode.core** is the foundation package, it contains the base classes
(CodeEdit, Mode, Panel) and a set of builtin modes and panels that are useful
for any kind of code editor. With pyqode.core you can already create a generic
code editor (similar to gedit, notepad++) with only a few lines of code.

Features
--------

Here are the core features:

- support multiple frontend: PyQt5, PyQt4 and PySide
- simple widget based on QPlainTextEdit
- easily customisable (modes and panels)
- native look and feel close to Qt creator
- builtin modes and panels (line number, code completion,
  syntax highlighting, code folding,...)
- Qt Designer plugin
- client/server architecture for smooth, non-blocking UI.


License
-------

pyQode is licensed under the MIT license.


Requirements
------------

pyqode.core depends on the following libraries:

-  Python 2 (>=2.7) or Python 3 (>= 3.2)
-  PyQt5 or PyQt4 or PySide
-  pygments


Installation
------------
You need to install PyQt or PySide by yourself.

Then you can install pyqode.core using **pip**::

    $ pip install pyqode.core

Testing
-------

pyqode.core now has a test suite and measure its coverage.

To run the tests, you must first install tox and pytest::

    $ pip install tox pytest

You might also want to install pytest-cov and pytest-pep8.

Then you can run the tests by running the following command::

    $ tox

To run the tests for a specifc environment, use the -e option. E.g. to run
tests with python 2.7 and pyqt4, you would run::

    $ tox -e py27-pyqt4

Here is the list of available test environments:

- py27-pyqt4
- py27-pyqt5
- py32-pyqt4
- py32-pyqt5
- py33-pyqt4
- py33-pyqt5
- py34-pyqt4
- py34-pyqt5
- cov
- pep8

Resources
---------

- `Downloads`_
- `Source repository`_
- `Documentation`_
- `Wiki`_


Snapshots
---------

Here are a few snapshots of the notepad example application (snapshots
taken on a Gnome 3 desktop):

.. image:: doc/source/_static/notepad.png
    :alt: Default style

.. image:: doc/source/_static/notepad-monokai.png
    :alt: Monokai style
    
    
.. _pyqode.core: https://github.com/pyQode/pyqode.core
.. _pyqode.python: https://github.com/pyQode/pyqode.python
.. _pyqode.designer: https://github.com/pyQode/pyqode.designer
.. _Downloads: https://github.com/pyQode/pyqode.core/releases
.. _Source repository: https://github.com/pyQode/pyqode.core/
.. _Documentation: http://pyqodecore.readthedocs.org/en/latest/
.. _Wiki: https://github.com/pyQode/pyqode.core/wiki
.. _master: https://github.com/pyQode/pyqode.core/tree/master
.. _develop: https://github.com/pyQode/pyqode.core/tree/develop
