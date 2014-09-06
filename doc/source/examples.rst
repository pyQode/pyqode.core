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

This is the most basic example. It starts and configures a very simple editor
with only a few modes and panels.

Frontend:
+++++++++

.. literalinclude:: /../../examples/simple/basic.py
   :linenos:

Backend:
++++++++

.. literalinclude:: /../../examples/simple/server.py
   :linenos:

Please note the the frontend script must be run with **python 3**. We do not
support python 2 for the frontend anymore but the backend must still be able
to be run with python 2 in order to support python 2 code completion and
linting in the editor (this is true only for pyqode.core and pyqode.python,
other languages such as cobol do not care about python 2 compatibility...)

Custom actions
--------------

This example show you how to modify default actions, here we modify the
shortcut and the text of the ``duplicate lines`` actions.

.. note:: This example shares the backend script with the Basic example.

.. literalinclude:: /../../examples/simple/custom_actions.py
   :linenos:

Change editor properties
------------------------

This example show you how to change some editor properties. Here we modify
the pygments color scheme.

.. note:: This example shares the backend script with the Basic example.

.. literalinclude:: /../../examples/simple/style_and_settings.py
   :linenos:


Notepad
-------

This example is a complete but minimal code editor application. It is too large
to be included here but you should really have a look at it as this example
combines nearly all the concepts exposed by pyqode.core
