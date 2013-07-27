PCEF - Python/Qt Code Editing Framework
==========================================

*version 1.0.0-beta* 

![alt text](https://travis-ci.org/ColinDuquesnoy/pcef-core.png?branch=develop "Travis-CI build status")
    
**Beta! The public API is stable but the documentation is not available at the moment. 
However the code already contains valuable comments and there are quite a few examples available in the examples directory)**

What is PCEF?
----------------

PCEF is a *flexible source code editing framework* for Python Qt applications.

*pcef-core* is the foundation package, it contains everything you need to create a 
generic (language independant) code editor widget and is the mandatory requirement for any pcef extension.

The base widget (QCodeEdit) is a simple extension of QPlainTextEdit that can be customised by adding 
extensions (modes and panels).


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
  * [language specific extensions](https://github.com/ColinDuquesnoy/pcef-core/wiki/Extensions)

License
---------

PCEF is licensed under the LGPL v3.


Requirements
--------------

pcef-core depends on the following libraries:
   
   * PyQt4 or PySide
   * Python 2.7 or Python 3 (>= 3.2)
   * pygments
   * setuptools

Installation
--------------

    $ pip install pcef-core
    
Usage
--------------

Here is a simple example using PyQt4:

```python
# simple example using PyQt4
import sys
import PyQt4
import pcef.core
from PyQt4.QtGui import QApplication


def main():
    app = QApplication(sys.argv)
	editor = pcef.core.QGenericCodeEdit()
	editor.openFile(__file__)
	editor.show()
	return app.exec_()


if __name__ == "__main__":
	sys.exit(main())
```

Screenshots
----------------

**TODO**
    
Resources
----------------

* [Downloads](https://github.com/ColinDuquesnoy/pcef-core/releases)
* [Source repository](https://github.com/ColinDuquesnoy/pcef-core/)
* [Documentation version 0.2](http://packages.python.org/PCEF)
* [Wiki](https://github.com/ColinDuquesnoy/pcef-core/wiki)
