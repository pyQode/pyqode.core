Getting started
===============

This page is a gentle introduction to the pyQode framework.

Before reading this you should have pyqode.core and PySide/PyQt4 :doc:`installed </download>` on your system.


.. contents:: :local:


Public API
--------------

The public API is fully exposed by the pyqode.core package.

You only need to import **pyqode.core** to get access to the entire public API::

    import pyqode.core
    code_edit = pyqode.core.QCodeEdit()
    text_deco = pyqode.core.TextDecoration()
    cc_mode = pyqode.core.CodeCompletionMode()
    line_nbr_panel = pyqode.core.LineNumberPanel()


Selecting a Qt bindings
------------------------

The first thing to do when using pyQode is to specify the Qt bindings you want to use for your application

There are multiple ways of doing this but the preferred way is to simply set an
environment variable at the top of your main module and then import pyqode.core::

    import os
    os.environ["QT_API"] = "PySide"  # or "PyQt" if you want to use PyQt4
    import pyqode.core


You can also specify it using the command line arguments:

.. code-block:: bash

    $ python your_script.py --PySide

or

.. code-block:: bash

    $ python your_script.py --PyQt

.. warning:: The QT_API string is case sensitive (this will change with version 1.1)


.. note:: You can also write a qt bindings independent application by using the **pyqode.qt** package.
          pyQode will pick up the first available bindings and expose it through the **qt** package.
          Simply import QtGui and QtCore module from pyqode.qt to use the automatically chosen binding:

          .. code-block:: python

              import sys
              from pyqode.qt import QtGui

              app = QtGui.QApplication(sys.argv)
              win = QtGui.QMainWindow()
              win.show()
              print(app)
              app.exec_()

**Most of the code samples of this documentation are bindings independent and use the pyqode.qt package.**


The editor widget: QCodeEdit
------------------------------

The editor widget is a simple extension to QPlainTextEdit.

It adds a few utility signals/methods and introduces the concept of **Modes and Panels**.

A mode/panel is an editor extension that, once installed on a QCodeEdit instance, may modify its behaviour and appearance:

  * **Modes** are simple objects which connect to the editor signals to add new behaviours (such as automatic indentation, code completion, syntax checking,...)

  * **Panels** are the combination of a **Mode** and a **QWidget**. They are displayed in the QCodeEdit's content margins.
    When you install a Panel on a QCodeEdit, you can choose to install it on one of the four following zones:

        .. image:: _static/editor_widget.png
            :align: center
            :width: 600
            :height: 450


pyQode tries to keep things simple for the basic user while not preventing advanced user from doing complex things.

There is actually two way to use pyqode:

    - use a pre-made editor that already fits your needs (QGenericCodeEdit)
    - use the raw editor widget and install your own selection of modes and panels.


.. note:: The editor widget is meant to work with files instead of raw text.
          Prefer to use the openFile/saveToFile methods instead of the
          setPlainText/plainText methods.

Using a pre-made editor
----------------------------

Usually, most of the pyqode packages will expose a pre-made code editor widget with
a set of modes and panels already installed.

pyqode.core exposes the **QGenericCodeEdit** widget, a widget that is suitable for a
language independent (not very smart) code editor widget.

Here is a minimal example code:

.. code-block:: python

    import sys
    from pyqode.qt import QtGui
    import pyqode.core


    def main():
        app = QtGui.QApplication(sys.argv)
        window = QtGui.QMainWindow()
        editor = pyqode.core.QGenericCodeEdit()
        editor.openFile(__file__)
        window.setCentralWidget(editor)
        window.show()
        sys.exit(app.exec_())


    if __name__ == "__main__":
        main()

Using the raw editor
---------------------

Using the raw QCodeEdit widget, you will be able to make your own selection of
modes and panels:

.. code-block:: python

    import sys
    from pyqode.qt import QtGui
    import pyqode.core


    def main():
        app = QtGui.QApplication(sys.argv)
        window = QtGui.QMainWindow()
        editor = pyqode.core.QCodeEdit()
        editor.openFile(__file__)
        editor.installMode(pyqode.core.PygmentsSyntaxHighlighter(editor.document()))
        editor.installPanel(pyqode.core.SearchAndReplacePanel(),
                            position=pyqode.core.PanelPosition.TOP)
        window.setCentralWidget(editor)
        window.show()
        sys.exit(app.exec_())


    if __name__ == "__main__":
        main()


Retrieving a mode/Panel
--------------------------------

Installed modes and panels are set as object attributes using their name property as the attribute key::

    editor = QCodeEdit()
    cc = CodeCompletionMode()
    cc.name = "cc"
    editor.installMode(CodeCompletionMode())
    print(editor.cc)


Changing the editor style and settings:
-------------------------------------------

Editor style and settings can be easily customised using the editor's style and settings properties:

.. code-block:: python

    editor = pyqode.core.QCodeEdit()
    editor.style.setValue("backgound", QtGui.QColor("#000000"))
    editor.settings.setValue("tabLength", 4)

Styling is more described in the :doc:`advanced </advanced>` section of the documentation
