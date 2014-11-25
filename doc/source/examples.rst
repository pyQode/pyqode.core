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


Modes
-----

Auto complete
+++++++++++++

.. literalinclude:: /../../examples/modes/autocomplete.py
   :linenos:

Auto indent
+++++++++++

.. literalinclude:: /../../examples/modes/autocomplete.py
   :linenos:

Caret line highlighter
++++++++++++++++++++++

.. literalinclude:: /../../examples/modes/caret_line_highlighter_with_syntax_highlighter.py
   :linenos:

.. literalinclude:: /../../examples/modes/caret_line_highlighter_without_syntax_highlighter.py
   :linenos:


Case converter
++++++++++++++

.. literalinclude:: /../../examples/modes/case_converter.py
   :linenos:

Checker (linter)
++++++++++++++++

.. literalinclude:: /../../examples/modes/checker.py
   :linenos:


Code completion
+++++++++++++++

.. literalinclude:: /../../examples/modes/code_completion_backend.py
   :linenos:

.. literalinclude:: /../../examples/modes/code_completion_frontend.py
   :linenos:

Extended selection
++++++++++++++++++

.. literalinclude:: /../../examples/modes/extended_selections.py
   :linenos:

File watcher
++++++++++++

.. literalinclude:: /../../examples/modes/filewatcher.py
   :linenos:

Indenter
++++++++

.. literalinclude:: /../../examples/modes/indenter.py
   :linenos:

Occurences highlighter
++++++++++++++++++++++

.. literalinclude:: /../../examples/modes/occurences.py
   :linenos:

Pygments syntax highligher
++++++++++++++++++++++++++

.. literalinclude:: /../../examples/modes/pygments_syntax_highlighter.py
   :linenos:

Righ margin
+++++++++++

.. literalinclude:: /../../examples/modes/right_margin.py
   :linenos:

Smart backspace
+++++++++++++++

.. literalinclude:: /../../examples/modes/smart_backspace.py
   :linenos:

Symbol matcher
++++++++++++++

.. literalinclude:: /../../examples/modes/symbol_matcher.py
   :linenos:


Zoom
++++

.. literalinclude:: /../../examples/modes/zoom.py
   :linenos:

Panels
------

Checker (linter)
++++++++++++++++

.. literalinclude:: /../../examples/panels/checker.py
   :linenos:

Code folding
++++++++++++

.. literalinclude:: /../../examples/panels/folding.py
   :linenos:

Global checker
++++++++++++++

.. literalinclude:: /../../examples/panels/global_checker.py
   :linenos:

Line numbers
------------

.. literalinclude:: /../../examples/panels/line_numbers.py
   :linenos:

Widgets
-------

Errors table
++++++++++++

.. literalinclude:: /../../examples/widgets/errors_table.py
   :linenos:


File system tree view
+++++++++++++++++++++

.. literalinclude:: /../../examples/widgets/filesystem_treeview.py
   :linenos:


Interactive console
+++++++++++++++++++

.. literalinclude:: /../../examples/widgets/interactive_process.py
   :linenos:

.. literalinclude:: /../../examples/widgets/interactive_console.py
   :linenos:


Splittable tab widget (generic version)
+++++++++++++++++++++++++++++++++++++++

.. literalinclude:: /../../examples/widgets/splittable_tab_widget.py
   :linenos:


Splittable tab widget (CodeEdit specialization)
+++++++++++++++++++++++++++++++++++++++++++++++

.. literalinclude:: /../../examples/widgets/splittable_codeedit_tab_widget.py
   :linenos:
