Python/Qt Code Editor Widget library
====================================

.. image:: https://api.travis-ci.org/pyQode/pyqode.core.png?branch=master
    :target: https://travis-ci.org/pyQode/pyqode.core
    :alt: Travis-CI build status

.. image:: https://pypip.in/d/pyqode.core/badge.png
    :target: https://crate.io/packages/pyqode.core/
    :alt: Number of PyPI downloads

.. image:: https://pypip.in/v/pyqode.core/badge.png
    :target: https://crate.io/packages/pyqode.core/
    :alt: Latest PyPI version

.. image:: https://badge.waffle.io/pyqode/pyqode.core.png?label=ready&title=Ready 
    :target: https://waffle.io/pyqode/pyqode.core
    :alt: 'Stories in Ready'

What is pyQode?
---------------

pyQode is a *flexible source code editor widget* for Python Qt
applications. **pyQode is a library/widget, not an IDE**. You can see it as an
alternative to QScintilla.


pyQode is a **namespace package** made up of the following official packages:

  - `pyqode.core`_: core package

  - `pyqode.python`_: python support (code completion, ...)

  - `pyqode.widgets`_: useful widgets for pyqode apps

  - `pyqode.designer`_: Starts Qt designer with all pyqode plugins

.. _pyqode.core: https://github.com/pyQode/pyqode.core
.. _pyqode.python: https://github.com/pyQode/pyqode.python
.. _pyqode.widgets: https://github.com/pyQode/pyqode.widgets
.. _pyqode.designer: https://github.com/pyQode/pyqode.designer

**pyqode.core** is the foundation package, it contains the pyqode base classes (QCodeEdit, Mode, Panel) 
and a set of builtin modes and panels that are useful for any kind of code editor. With pyqode.core you 
can already create a generic code editor (similar to gedit, notepad++) with only a few lines of code.

Features
--------

Here are the core features:

-  simple widget based on QPlainTextEdit
-  easily customisable (modes and panels)
-  native look and feel close to Qt creator
-  builtin modes and panels (folding, line number, code completion,
   syntax highlighting)
-  Qt Designer plugin


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
You need to install PyQt4 or PySide by yourself.

Then you can install pyqode using pip::

    $ pip install pyqode.core


Usage
-----

The *public API* is exposed by the *pyqode.core* package.

Here is a `simple example using PyQt4`_:

.. code:: python

    # simple example using PyQt4
    import sys
    import PyQt4  # just to tell pyqode we want to use PyQt4.
    import pyqode.core
    from PyQt4.QtGui import QApplication


    def main():
        app = QApplication(sys.argv)
        editor = pyqode.core.QGenericCodeEdit()
        editor.openFile(__file__)
        editor.resize(800, 600)
        editor.show()
        return app.exec_()


    if __name__ == "__main__":
        sys.exit(main())

.. _simple example using PyQt4: https://gist.github.com/ColinDuquesnoy/6096185

Resources
---------

-  `Downloads`_
-  `Source repository`_
-  `Documentation`_
-  `Wiki`_

.. _Downloads: https://github.com/pyQode/pyqode.core/releases
.. _Source repository: https://github.com/pyQode/pyqode.core/
.. _Documentation: http://pyqodecore.readthedocs.org/en/latest/
.. _Wiki: https://github.com/pyQode/pyqode.core/wiki


Screenshots
-----------

Here are a few screenshots of the gui integration example on several different platforms:

* Windows 7:

.. image:: https://raw.github.com/ColinDuquesnoy/pyqode.core/master/screenshots/windows7.PNG
    :alt: Windows 7
    
* Ubuntu:

.. image:: https://raw.github.com/ColinDuquesnoy/pyqode.core/master/screenshots/ubuntu.png
    :alt: Ubuntu
    
* Linux Mint:

.. image:: https://raw.github.com/ColinDuquesnoy/pyqode.core/master/screenshots/mint.png
    :alt: Linux mint
    
* KDE:

.. image:: https://raw.github.com/ColinDuquesnoy/pyqode.core/master/screenshots/kde.png
    :alt: KDE
    
* KDE with a dark color scheme:

.. image:: https://raw.github.com/ColinDuquesnoy/pyqode.core/master/screenshots/kde-dark.png
    :alt: KDE dark
    
* Gnome:

.. image:: https://raw.github.com/ColinDuquesnoy/pyqode.core/master/screenshots/gnome.png
    :alt: Gnome


