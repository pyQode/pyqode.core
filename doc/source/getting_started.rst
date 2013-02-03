Getting started
===============

.. contents:: :local:

This framework aims to keep things simple for the basic user while not preventing advanced user from doing more
complex things.

For that purpose, there is two way to use pcef:

    - using a pre-made editor that already fits your needs (from pcef.editors import)
    - using a raw editor widget where you can install the modes/panels you really need.

In both cases user will always have a way to add a new mode/panel or to disable already installed one.

Using a pre-made editor
----------------------------

The pcef.editors modules contains a series of pre-made editors.

A pre-made editor is an editor widget with a set of installed modes and panels.
At the moment, there is only one editor: QGenericEditor.

Here is a minimal example code:


.. highlight:: python

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


