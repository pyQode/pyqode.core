PySide Code Editing Framework
=====================================

PCEF is code editing framework for PySide applications. It provides a flexible code editor ready to use in any PySide
applications. Flexibility is achieved through a system of editor extensions (custom panels and modes).

At the moment, the framework only provides a generic code editor (language independent) but plans are to at least
provides full support for python and maybe c++.

Here are the core features:

 * **syntax highlighting mode** (using pygments)
 * **code completion** (static word list, from document words)
 * line number Panel
 * **code folding** Panel
 * markers Panel (to add breakpoints, bookmarks, errors,...)
 * right margin indicator mode
 * active line highlighting mode
 * **editor zoom** mode
 * find and replace Panel
 * **text decorations** (squiggle, box)
 * unicode support (specify encoding when you load your file)
 * **easy styling** (built-in white and dark styles + possibility to customize using **JSON style schemes**)
 * **flexible framework** to add custom panels/modes
 * auto indent mode(indentation level is based on the previous line indent)

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

.. highlight:: python

Here is a simple example::

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


Screenshots
--------------

    .. image:: /doc/source/_static/white_style.png

    .. image:: /doc/source/_static/dark_style.png
