Python/Qt Code Editor Widget library
======================================================

*version 1.0.0-beta*

.. image:: https://api.travis-ci.org/ColinDuquesnoy/pyqode-core.png?branch=master
    :target: https://travis-ci.org/ColinDuquesnoy/pyqode-core
    :alt: Travis-CI build status

What is pyQode?
-------------

pyQode is a *flexible source code editor widget* for Python Qt
applications. **pyQode is a library/widget, not an IDE**.

*pyqode-core* is the foundation package, it contains everything you need
to create a generic (language independent) code editor widget. It is the
mandatory requirement for any pyQode extension.

The base widget (QCodeEdit) is a simple extension of QPlainTextEdit that
can be customised by adding extensions (modes and panels).

Features
--------

Here are the core features:

-  supports PySide and PyQt4
-  supports Python 2 and Python 3
-  simple widget based on QPlainTextEdit
-  easily customisable (modes and panels)
-  native look and feel close to Qt creator
-  builtin modes and panels (folding, line number, code completion,
   syntax highlighting)
-  Qt Designer plugin
-  `language specific extensions`_

.. _language specific extensions: https://github.com/ColinDuquesnoy/pyqode-core/wiki/Extensions


License
-------

pyQode is licensed under the LGPL v3.

Requirements
------------

pyqode-core depends on the following libraries:

-  PyQt4 or PySide
-  Python 2.7 or Python 3 (>= 3.2)
-  pygments
-  setuptools

Installation
------------

::

    $ pip install pyqode-core

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
-  `Documentation`_ *(outdated)*
-  `Wiki`_

.. _Downloads: https://github.com/ColinDuquesnoy/pyqode-core/releases
.. _Source repository: https://github.com/ColinDuquesnoy/pyqode-core/
.. _Documentation : http://packages.python.org/PCEF
.. _Wiki: https://github.com/ColinDuquesnoy/pyqode-core/wiki

Screenshots
------------

Here are a few screenshots of the gui integration example on several different platforms:

* Windows 7:

.. image:: https://raw.github.com/ColinDuquesnoy/pyqode-core/master/screenshots/windows7.PNG
    :alt: Windows 7
    
* Ubuntu:

.. image:: https://raw.github.com/ColinDuquesnoy/pyqode-core/master/screenshots/ubuntu.png
    :alt: Ubuntu
    
* Linux Mint:

.. image:: https://raw.github.com/ColinDuquesnoy/pyqode-core/master/screenshots/mint.png
    :alt: Linux mint
    
* KDE:

.. image:: https://raw.github.com/ColinDuquesnoy/pyqode-core/master/screenshots/kde.png
    :alt: KDE
    
* KDE with a dark color scheme:

.. image:: https://raw.github.com/ColinDuquesnoy/pyqode-core/master/screenshots/kde-dark.png
    :alt: KDE dark
    
* Gnome:

.. image:: https://raw.github.com/ColinDuquesnoy/pyqode-core/master/screenshots/gnome.png
    :alt: Gnome
