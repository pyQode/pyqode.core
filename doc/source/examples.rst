Examples
========
If you downloaded a source archive or cloned pyQode from github, you will find a
series of examples in the examples directory at the root of the archive.

All examples requires pyqode.core to be installed.

.. note:: All examples are bindings independent so that all user can run them
          without being required to install an unwanted qt binding.

.. contents:: :local:

.. highlight:: python
   :linenothreshold: 5

Using a pre-made editor
-----------------------

This example show how to use a pre-made editor.

.. literalinclude:: /../../examples/premade.py
   :linenos:

Creating a custom editor
----------------------------

This example show how to create a custom editor from scratch using the available
modes and panels.

.. literalinclude:: /../../examples/custom.py
   :linenos:

Gui integration
-----------------

This simple example show how you can build a simple generic editor using
pyqode.core. The example user interface has been designed in Qt Designer using
the pyqode.core plugins to add the QGenericCodeEdit to the ui.

.. literalinclude:: /../../examples/gui_integration/simple_editor.py
   :linenos:

.. note:: This example makes use of a designer ui file compiled using the
          translate_ui script. This script call the pyside compiler and replace
          a few imports to make it usable by both bindings. You typically don't
          need to do that in a real world application where you use one qt
          binding.

Force PyQt5
----------------

This example shows you how you can force pyQode to use PyQt5.

.. literalinclude:: /../../examples/qt_bindings/PyQt5.py
   :linenos:

Force PySide
----------------

This example shows you how you can force pyQode to use PySide.

.. literalinclude:: /../../examples/qt_bindings/pyside.py
   :linenos:

Dump style and settings
-------------------------

This example dumps the style and settings property registry of a simple
CodeEdit and a QGenericCodeEdit to show you the dynamic nature of the settings
depending on the installed modes/panels.

.. literalinclude:: /../../examples/styling/dump.py
   :linenos:

Save and load settings
-------------------------

This example show you how you can serialize/deserialize style and settings
properties. The example create a first editor and modify its style manually. The
style is then save to a json file and used to setup a second editor.

.. literalinclude:: /../../examples/styling/save_load.py
   :linenos:
