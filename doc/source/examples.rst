Examples
========
If you downloaded a source archive or cloned pyQode from github, you will find a
series of examples in the ``examples`` directory, at the root of the archive.

All examples requires pyqode.core to be installed.

.. note:: All examples are bindings independent so that every user can run them
          without being required to install an unwanted qt binding.

.. highlight:: python
   :linenothreshold: 5

Basic example
-------------

This example show how to use a pre-made editor.

Frontend:
+++++++++

.. literalinclude:: /../../examples/simple/basic.py
   :linenos:

Backend:
++++++++

.. literalinclude:: /../../examples/simple/server.py
   :linenos:

Custom actions
--------------

This example show you how to modify default actions, here we modify the
shortcut and the text of the ``duplicate lines`` actions.

.. note:: This example shares the backend script with the Basic example.

.. literalinclude:: /../../examples/simple/custom_actions.py
   :linenos:

Custom actions
--------------

This example show you how to change some editor properties. Here we modify
the pygments color scheme.

.. note:: This example shares the backend script with the Basic example.

.. literalinclude:: /../../examples/simple/style_and_settings.py
   :linenos:

Select Qt bindings
------------------

Those examples show you how to force the use of a specific qt bindings.

PyQt5 (default)
+++++++++++++++

.. literalinclude:: /../../examples/select_qt/pyqt5.py
   :linenos:

PyQt4
+++++

.. literalinclude:: /../../examples/select_qt/pyqt4.py
   :linenos:

PySide
++++++

.. literalinclude:: /../../examples/select_qt/pyside.py
   :linenos:

Notepad
-------

This example is a complete but minimal code editor application. It is too large
to be included here. You should really have a look at it as this example
combines nealy all the concepts exposed by pyqode.core