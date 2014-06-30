Advanced topics
===============

This page covers advanced topics:

Creating modes and panels
-------------------------
In this section we will see how to extend pyqode with new modes and panels,
covering the creation of a new mode/panel from scratch and from an existing one.

pyQode tends to prefer composition over inheritance, that's why you should
create a new mode/panel whenever you want to extends the functionality of
CodeEdit.

You do that by subclassing :class:`pyqode.core.api.Mode` or
:class:`pyqode.core.api.Panel` (or a more specific Mode such as the
SyntaxHighlighterMode)

There are a few methods that are interesting to override:

   * **on_state_changed** :

     This method is called when the mode/panel is disabled/enabled.
     *It is guarantied to be called when the mode/panel is installed on an
     editor instance.*

     Typically you use this method to connect/disconnect to/from the editor's
     signals::

        def on_state_changed(self, state):
            super(MyMode, self)._onStateChanged(state)
            if state:
                pass # connect to editor's signals
                # self.editor.cursorPositionChanged.connect(self.myMethod)
            else:
                pass # diconnect from the editor's signals
                # self.editor.cursorPositionChanged.disconnect(self.myMethod)

   * **on_install**:

     This method is called when the mode is installed on CodeEdit.

Simple modes and panels
-----------------------

Here some code templates that you can use as a starting point to create
simple modes and panels:

* Mode:

.. code-block:: python

    from pyqode.core import api

    class MyMode(api.Mode):

        def on_install(self, editor):
            super().on_install(editor)
            # initialise some stuff here
            pass

        def on_state_changed(self, state):
            super().on_state_changed(state)
            if state:
                pass  # mode enabled, time to connect to signals
            else:
                pass  # mode disabled, time to disconnect from signals

* Panel:

.. code-block:: python

    from pyqode.core import api

    class MyPanel(api.Panel):

        def __init__(self):
            super().__init__()
            # setup your ui here (you may use ui designed in Qt Designer)
            pass

        def on_install(self, editor):
            super().on_install(editor)
            # initialise some stuff here
            pass

        def on_state_changed(self, state):
            super().on_state_changed(state)
            if state:
                pass  # mode enabled, time to connect to signals
            else:
                pass  # mode disabled, time to disconnect from signals


Code checker modes (code linting)
---------------------------------

pyQode have already have a mode to help you write code checker modes (linters):
:class:`pyqode.core.modes.CheckerMode`

To create a new checker mode, simply subclass :class:`pyqode.core.modes.CheckerMode` and
pass it the checker function that needs to be executed contextually (on the
backend side).

Here is a typical implementation of a checker mode:

.. code-block:: python

    from pyqode.core import modes


    def run_my_linter(q, code, filePath, fileEncoding):
        """
        This function is run by the backend process to lint some code

        :param code: The code to check
        :param filePath: the file path of the source code
        :param fileEncoding: the file encoding of the source code
        """
        messages = []
        # objects must be json serialisable (i.e. primitives)
        messages.append(("A warning", 1, 10))
        messages.append(("An error", 2, 17))
        # pass the results to the parent process
        return messages


    class MyCheckerMode(modes.CheckerMode):

        def __init__(self):
            super().__init(run_my_linter, clear_on_request=False)


Code completion modes
---------------------

The code completion mode is a flexible mode that provides a list of code
suggestions to the user. The list of suggestion is made up by collecting the
suggestions provided by a series of providers (this is done by the backend
process).

The only step required to add code completion support for your
favorite language is to implement a new CodeCompletionProvider that returns a
list of suggestions and set it on
:class:`pyqode.core.backend.CodeCompletionWorker`(on the backend side).

Here is the interface you must implement for a new code completion provider::

    class Provider(object):
        """
        This class describes the expected interface for code completion
        providers.

        You can inherit from this class but this is not required as long as you
        implement a ``complete`` method which returns the list of completions
        and have the expected signature::

            def complete(self, code, line, column, path, encoding, prefix):
                pass

        """

        def complete(self, code, line, column, path, encoding, prefix):
            """
            Returns a list of completions.

            A completion is dictionary with the following keys:
                - 'name': name of the completion, this the text displayed and
                inserted when the user select a completion in the list
                - 'icon': an optional icon file name
                - 'tooltip': an optional tooltip string

            :param code: code string
            :param line: line number (1 based)
            :param column: column number (0 based)
            :param path: file path
            :param encoding: file encoding
            :param prefix: completion prefix (text before cursor)

            :returns: A list of completion dicts as described above.
            :rtype: list
            """
            raise NotImplementedError()


To set it on the worker, just add the following lines to your backend server
script::

    from pyqode.core import backend

    backend.CodeCompletionWorker.providers.append(
        MyProvider())



Syntax highlighter mode
-----------------------

pyQode makes extensive use of QSyntaxHighlighter for various purposes,
sometimes completely different from syntax highlighting such as code folding and
parenthesis matching.

To implement a new syntax highlighter for CodeEdit, you **must subclass**
:class:`pyqode.core.api.SyntaxHighlighter` and **override** ``highlight_block``
instead of ``highlightBlock``.

For a complete real life example, see :class:`pyqode.core.modes.PygmentsSyntaxHighlighter`
or :class:`pyqode.python.PythonSyntaxHighlighters`

.. warning:: You cannot just create your own QSyntaxHighlighter as you would do
             with a simple QPlainTextEdit because this will break code folding
             and parenthesis matching modes!

Code folding
------------

**Code folding has been temporarly removed from pyqode 2.0. It will be reintroduced in a future version.**


Designer plugins
----------------

pyQode comes with a mechanism to quickly create Qt designer plugins and most
of the widgets already have their own plugin.

To use the existing pyQode plugins you need to use the `pyqode.designer`_ startup
script. This scripts discovers all installed pyqode plugins using pkgconfig and
starts Qt Designer with the correct plugins path.

A pyQode Qt Designer is a Qt designer plugin but also a setuptools plugin (
using the entry points mechanism).

This section will tell you how to create your own Designer plugin and make it
available to the startup script.

For that you need to create a python module for you plugin following this
scheme (example for the Python code edit, from pyqode.python):


.. code-block:: python

    from pyqode.python.code_edit import PyCodeEdit
    from pyqode.core.designer_plugins import WidgetPlugin


    class PyCodeEditPlugin(WidgetPlugin):
        def klass(self):
            return PyCodeEdit

        def objectName(self):
            return 'pyCodeEdit'


Now that you have a script you must install it as a **pyqode_plugins**.
To do that, you just have to append an entrypoint to your setup.py:

.. code-block:: python

    setup(
        ...
        entry_points={'pyqode_plugins':
                     ['your_plugin_module = your_package.your_plugin_module']},
        ...
        )


.. _`pyqode.designer`:

.. warning:: It is important that your plugin module file name ends up with
    ``plugin``. See `this document`_ for more information about QtDesigner
    plugins.

.. _this document: http://pyqt.sourceforge.net/Docs/PyQt5/designer.html#writing-qt-designer-plugins