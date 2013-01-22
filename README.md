PySide Code Editing Framework
=====================================

Provides a flexible framework to develop code editing tools with PySide.

It provides an editor widget ready to be used in any PySide applications.

The widget can be customised with custom/pre-made panels and modes.


Here are some [screenshots](https://www.dropbox.com/sh/f0xpcu5zapciuma/Ef10GaBnhD)


Features
-----------


Here is the features list:

 * syntax highlighting (using pygments)
 * line number panel
 * code folding panel
 * markers panel (to add breakpoints, bookmarks, errors,...)
 * right margin indicator
 * active line highlighting
 * find and replace panel
 * text decorations (squiggle, box)
 * unicode support (specify encoding when you load your file)
 * styling (builtin white and dark styles + possibility to customize)
 * flexible framework to add custom widgets or specific behaviour

Plans are to to add code completion and python support (using rope, pylint,...)

License
---------

LGPL v3

Installation
--------------


The first release of the package is not finished yet but you can clone the
project and execute example.py (require PySide to be installed)


Usage
--------


Here is a simple example:

```python
#!/usr/bin/env python2  # python 2 only at the moment
import sys

from PySide.QtGui import QApplication
from PySide.QtGui import QMainWindow

from pcef import openFileInEditor
from pcef.editors import QGenericEditor


def main():
    """ Application entry point """
    # create qt objects (app, window and our editor)
    app = QApplication(sys.argv)
    window = QMainWindow()
    editor = QGenericEditor()
    window.setCentralWidget(editor)

    # open a file
    openFileInEditor(editor, __file__)

    # run
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
```
