PCEF: Python/Qt Code Editing Framework
=====================================

*version 1.0.0-beta* 

.. image:: https://travis-ci.org/ColinDuquesnoy/pcef-core.png?branch=develop
    :target: https://travis-ci.org/ColinDuquesnoy/pcef-core
    :alt: Travis-CI build status
    
**Beta! The public API is stable but the documentation is not available at the moment. 
However the code already contains valuable comments and there are quite a few examples available in the examples directory)**

What is PCEF?
----------------

PCEF is a flexible source code editing framework for Python Qt applications.

**pcef-core** is the foundation package, it contains everything you need to create a 
generic (language independant) code editor widget.

The base widget is a simple extension of QPlainTextEdit that can be customised by adding extensions (modes and panels).


Features
-------------

Here are the core features:

  * supports PySide and PyQt4
  * supports Python 2 and Python 3
  * simple widget based on QPlainTextEdit
  * easily customisable (modes and panels)
  * native look and feel close to Qt creator
  * builtin modes and panels (folding, line number, code completion, syntax highlighting)
  * Qt Designer plugin
  * language specific extensions (see the wiki)

License
---------

PCEF is licensed under the LGPL v3.

_Note that is you use the PyQt backend, you will have to comply with the GPL license._

Requirements
--------------

pcef-core depends on the following libraries:
   
   * PyQt4 or PySide
   * Python 2.7 or Python 3 (>= 3.2)
   * pygments
   * setuptools

Installation
--------------

You can install pcef-core using pip or easy_install::

    pip install pcef-core
    
Resources
------------

* Source repository: https://github.com/ColinDuquesnoy/pcef-core/
* Documentation: http://packages.python.org/PCEF (version 0.2!)
* Package repository: http://pypi.python.org/pypi/pcef-core/
