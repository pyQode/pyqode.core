PySide Code Editing Framework
=====================================

PCEF is code editing framework for PySide applications. It provides a flexible code editor that you can just drop in any PySide
applications. Flexibility is achieved through a system of editor extensions (custom panels and modes).

The framework also provides two pre-configurededitors:
* a generic (langage independent) editor widget
* a python editor widget

Here are the core features (used in the generic editor):

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

Here are the python specific features:

* accurate code completion using **Jedi**
* calltips (using Jedi too)
* on the fly syntax checking (pylint + pyflakes + pep8)


License
---------

PCEF is licensed under the LGPL v3.

Installation
--------------

PCEF is hosted on pypi. You can installing using pip (you need to have setuptools and PySide already installed)::

    pip install PCEF

To run the examples, execute one of the following commands::
    
    pcef_generic_example

You can also clone the repository or download the source archive and install the package manually::
    
    python setup.py install

To run the examples run the one of the following scripts (you don't need to install pcef to run the examples):

- run_generic_example.py

Resources
------------

* Source repository: https://github.com/ColinDuquesnoy/PCEF/
* Documentation: http://packages.python.org/PCEF
* Package repository: http://pypi.python.org/pypi/PCEF/0.1.0


Usage
--------

.. highlight:: python

Here is a simple example::

    #!/usr/bin/env python2  # python 2 only at the moment
    import sys

    from PySide.QtGui import QApplication
    from PySide.QtGui import QMainWindow

    from pcef import openFileInEditor
    from pcef.editors import GenericEditor


    def main():
        """ Application entry point """
        # create qt objects (app, window and our editor)
        app = QApplication(sys.argv)
        window = QMainWindow()
        editor = GenericEditor()
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

* Default white style:

.. image:: /doc/source/_static/white_style.png

* Default dark style (inspired from the Darcula theme (Pycharm)):

.. image:: /doc/source/_static/dark_style.png
