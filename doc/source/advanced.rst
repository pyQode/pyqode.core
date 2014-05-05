Advanced topics
==================

This page covers advanced topics:

.. contents:: :local:

Styling
----------

pyQode use the PropertyRegistry class to store style and settings properties.
A property registry is a simple **dictionary of properties** (key/values)
organised per section. It can be easily serialised to **JSON**.

CodeEdit defines a series of style/settings properties in the "General"
section. Modes and panels are also free to add their properties when they are
installed on an editor instance. This means that you'll end up with completely
different dictionaries depending on the installed modes/panels.

For example, consider the difference between the CodeEdit and the
QGenericCodeEdit settings:

    * CodeEdit:
        .. code-block:: json

            {
                "General": {
                    "minIndentColumn": "0",
                    "showWhiteSpaces": "False",
                    "tabLength": "4",
                    "useSpacesInsteadOfTab": "True"
                }
            }

    * QGenericCodeEdit:

        .. code-block:: json

            {
                "Code completion": {
                    "caseSensitive": "False",
                    "showTooltips": "True",
                    "triggerKey": "32",
                    "triggerKeys": "[46]",
                    "triggerLength": "1",
                    "triggerSymbols": "[.]"
                },
                "General": {
                    "autoReloadChangedFiles": "False",
                    "minIndentColumn": "0",
                    "rightMarginPos": "80",
                    "showWhiteSpaces": "False",
                    "tabLength": "4",
                    "useSpacesInsteadOfTab": "True"
                }
            }


.. note:: To know the list of properties available for a specific configuration,
          you can always dump the style and settings dictionaries to a JSON
          string::

            print(editor.settings.dump())
            print(editor.style.dump())

Changing a property manually:
+++++++++++++++++++++++++++++++++++++++++++

You can change the style and settings values using the style and settings
properties of CodeEdit:

.. code-block:: python

    editor.style.setValue("background", QColor("#FF5436"))
    editor.settings.setValue("showWhiteSpaces", True))

When you change a value, a signal is emitted so that the concerned modes/panels
can adapt their brushes, pens, stylesheets,... This is important to consider
when you create a new mode/panel that depends on such properties.

Save/Load from file:
+++++++++++++++++++++++++++++++++++++++++++

Style and settings can be serialized to JSON easily:

.. code-block:: python

    # Editor 01: modify default style to be dark then save it to "dark.json"
    file_path = "dark.json"
    editor_01 = pyqode.core.CodeEdit()
    editor_01.style.setValue("background", "#222222")
    editor_01.style.setValue("foreground", "#888888")
    editor_01.style.save(file_path)

    # Editor 02: style loaded from the file we just saved
    editor_02 = pyqode.core.CodeEdit()
    editor_02.style.open(file_path)
    editor_02.show()


Creating modes and panels
-------------------------------------
In this section we will see how to extend the pyqode with new modes and panels,
covering the creation of a new mode/panel from scratch and from an existing one.

pyQode tends to prefer composition over inheritance, that's why you should
create a new mode/panel whenever you want to extends the functionality of
CodeEdit.

You do that by subclassing **pyqode.core.Mode** or **pyqode.core.Panel** (or a
more specific Mode such as the SyntaxHighlighterMode)

When you create a new mode you must give it an IDENTIFIER and a DESCRIPTION::

    class MyMode(Mode):
        IDENTIFIER = "myOwnMode"
        DESCRIPTION = "An example mode"

The IDENTIFIER string is set as the mode name and is used to identify the mode
when installed on a CodeEdit::

    editor.installMode(MyMode())
    print(editor.myOwnMode)

There are a few methods that are interesting to override:

   * **_onStateChanged** :

     The _onStateChanged method is called when the mode/panel is disabled/enabled.
     *It is guarantied to be called when the mode/panel is installed on an editor instance.*

     Typically you use this method to connect/disconnect to/from the editor's
     signals:

     .. code-block:: python

        def _onStateChanged(self, state):
            super(MyMode, self)._onStateChanged(state)
            if state:
                pass # connect to editor's signals
                # self.editor.cursorPositionChanged.connect(self.myMethod)
            else:
                pass # diconnect from the editor's signals
                # self.editor.cursorPositionChanged.disconnect(self.myMethod)

   * **_onInstall**:

     This method is called when the mode is installed on a CodeEdit.

     Typically, this method is used to add new properties to the editor style or
     settings:

        .. code-block:: python

            def _onInstall(self, editor):
                super(MyMode, self)._onInstall(editor)
                editor.settings.addProperty("myProperty", 4, section="mySection")

   * **_onStyleChanged**:

     This method is called whenever a style property has changed. Note that it is
     also called when the whole style changed (due to an affectation or when it
     is loaded from file).

     Here is the typical implementation:

        .. code-block:: python

            def _onStyleChanged(self, section, key):
                super(MyMode, self)._onStyleChanged(section, key)
                if (key == "myKey" and section == "mySection") or key is None:
                    value = self.editor.settings.value(key, section)
                    # do something with the new value


   * **_onStyleChanged**:

     This method is called whenever a settings property has changed. Note that it is
     also called when the whole settings changed (due to an affectation or when it
     is loaded from file).

     Here is the typical implementation:

        .. code-block:: python

            def _onSettingsChanged(self, section, key):
                super(MyMode, self)._onStyleChanged(section, key)
                if (key == "myKey" and section == "mySection") or key is None:
                    value = self.editor.settings.value(key, section)
                    # do something with the new value


Simple modes and panels
+++++++++++++++++++++++++++++

Here some code templates that you can use as a starting point to create
simple modes and panels:

* Mode:

.. code-block:: python

    import pyqode.core

    class MyMode(pyqode.core.Mode):
        IDENTIFIER = "myMode"
        DESCRIPTION = "Your mode description comes here"

        def _onInstall(self, editor):
            super(MyMode, self)._onInstall(editor)
            # add custom style/settings to the editor here

        def _onStateChanged(self, state):
            super(MyMode, self)._onStateChanged(editor)
            if state:
                pass  # mode enabled, time to connect to signals
            else:
                pass  # mode disabled, time to disconnect from signals

        def _onStyleChanged(section, key):
            super(MyMode, self)._onStyleChanged(section, key)
            pass  # you can update some style options here

        def _onSettingsChanged(section, key):
            super(MyMode, self)._onSettingsChanged(section, key)
            pass  # you can update some settings options here

* Panel:

.. code-block:: python

    import pyqode.core

    class MyPanel(pyqode.core.Panel):
        IDENTIFIER = "myPanel"
        DESCRIPTION = "Your panel description comes here"

        def __init__(self):
            super(MyPanel, self).__init__()
            # here you can setup your ui manually or using a Qt Designer ui file

        def _onInstall(self, editor):
            super(MyPanel, self)._onInstall(editor)
            # add custom style/settings to the editor here

        def _onStateChanged(self, state):
            super(MyPanel, self)._onStateChanged(editor)
            if state:
                pass  # mode enabled, time to connect to signals
            else:
                pass  # mode disabled, time to disconnect from signals

        def _onStyleChanged(section, key):
            super(MyPanel, self)._onStyleChanged(section, key)
            pass  # you can update some style options here

        def _onSettingsChanged(section, key):
            super(MyPanel, self)._onSettingsChanged(section, key)
            pass  # you can update some settings options here


Code checker modes
++++++++++++++++++++++

pyQode have a base mode to help you write code checker modes: pyqode.core.CheckerMode

To create a new checker mode, you can simply subclass CheckerMode and pass him
the checker function that needs to be executed contextually. The CheckerMode will
actually execute this function in a background process. Its role is to run the
code analysis and to collect a series of CheckerMessage, appended to a
multiprocessing.Queue .

Here is a typical implementation of a checker mode:

.. code-block:: python

    import pyqode.core


    def checkerFunction(q, code, filePath, fileEncoding):
        """
        This function is run in a background process to check the code passed in
        the parameters.

        :param q: multiprocessing.Queue used to return the list of checker
                  messages
        :param code: The code to check
        :param filePath: the file path of the source code
        :param fileEncoding: the file encoding of the source code
        """
        messages = []
        messages.append(CheckerMessage("A warning",
                                       pyqode.core.MSG_STATUS_WARNING, 1))
        messages.append(CheckerMessage("An error",
                                       pyqode.core.MSG_STATUS_ERROR, 17))
        # pass the results to the parent process
        q.put(messages)


    class MyCheckerMode(CheckerMode):
        DESCRIPTION = "A checker mode example"
        IDENTIFIER = "myCheckerMode"

        def __init__(self):
            super(MyCheckerMode, self).__init(checkerFunction,
                                              clearOnRequest=False)

.. note:: Checker requests are configurable:

            * **pyqode.core.CHECK_TRIGGER_TXT_CHANGED**: the checker function will run every time the text changed and the user is idle (i.e. not typing some text)

            * **pyqode.core.CHECK_TRIGGER_TXT_SAVED**: the checker function will only run when the user save the editor's content.

Code completion modes
++++++++++++++++++++++

The code completion mode is a flexible mode that provides a list of code
suggestions to the user. The list of suggestion is made up by collecting the
suggestions provided by a series of CodeCompletionProvider. The code completion
mode run the CodeCompletionProvider in a background process. This background
process is started automatically the first time a CodeCompletionMode is installed
on a CodeEdit instance and shutdown when the QApplication is about to exit.

It is up to the user to install a completion provider on the completion mode.

That means that the only thing required to add code completion support for your
favorite language is to subclass CodeCompletionProvider to return a list of
contextual suggestions:

.. code-block::python

    import pyqode.core

    class MyCompletionProvider(pyqode.core.CodeCompletionProvider):
        def complete(code, line, column, completionPrefix, filePath, fileEncoding):
            """
            Returns a list of pyqode.core.Completion
            """
            completions = []
            completions.append(pyqode.core.Completion("First Suggestion"))
            completions.append(pyqode.core.Completion("A second one"))
            completions.append(pyqode.core.Completion("Hoho, even a third one"))
            return completions

.. note:: As the code completion provider is run in a background thread, you
          should not rely on object's attributes (e.g. to store previous results),
          instead you should use the processDict attribute:

          .. code-block::python

              class MyCompletionProvider(pyqode.core.CodeCompletionProvider):
                  def complete(code, line, column, completionPrefix, filePath, fileEncoding):
                      """
                      Returns a list of pyqode.core.Completion
                      """
                      completions = []
                      if "prev_results" in self.processDict:
                          return self.processDict["prev_result"]
                      completions.append(pyqode.core.Completion("First Suggestion"))
                      completions.append(pyqode.core.Completion("A second one"))
                      completions.append(pyqode.core.Completion("Hoho, even a third one"))
                      self.processDict["prev_result"] = completions
                      return ret_val

Syntax highlighter modes
+++++++++++++++++++++++++

pyQode makes extensive use of QSyntaxHighlighter for various purposes completely
different from syntax highlighting such as code folding and parenthesis matching.

To implement a new syntax highlighter for CodeEdit, you **must** subclass
pyqode.core.SyntaxHighlighter and override doHighlightBlock instead of
highlightBlock.

For a complete/real life example, see the pyqode.core.PygmentsSyntaxHighlighter
or the pyqode.python.PythonSyntaxHighlighters.

.. warning:: You cannot just create your own QSyntaxHighlighter as you would do
             with a simple QPlainTextEdit as this will break the code folding
             and parenthesis matching modes).

Code folding
+++++++++++++++++++++++++

To implement a new code folding algorithm, you just have to set your own
FoldDetector on the a syntax highlighter mode.

Code folding works using the concept of fold indent::

    A code folding marker will appear the line *before* the one where
    the indention level increases. The code folding region will end
    in the last line that has the same indention level (or higher),
    skipping blank lines.


Here is how to create a new fold detector:

.. code-block:: python

    import pyqode.core

    class DummyFoldDetector(pyqode.core.FoldDetector):
        def getFoldIndent(self, highlighter, block, text):
        """
        Returns the fold indent of a QTextBlock, here we simply return the
        line indent level.

        :param highlighter: Reference to the syntax highlighter mode
        :param block: Block to parse
        :param text: Text of the block (for convenience)
        :return: int
        """
        return len(text) - len(text.lstrip())

At the moment, there is already two specific FoldDetector:
    * one based on the line indent (but a little more evolved): good for python like languages
    * one based on string delimiters (e.g. '{', '}'): good for c like languages

Designer plugins
--------------------

pyQode comes with a mechanism to quickly create Qt designer plugins and most
of the widgets already have their own plugin. To use the existing pyQode plugins
you need to use the `pyqode.designer`_ startup script. This scripts discover the
pyqode plugins using pkgconfig and starts Qt Designer with the correct plugins
path. A pyQode Qt Designer is thus a Qt designer plugin but also a setuptools
plugin (using the entry points mechanism).

This section will tell you how to create your own Designer script and make it
available to the startup script.

For that you need to create a python module for you plugin following this scheme:


.. code-block:: python

    # This only works with PyQt, PySide does not support the QtDesigner module
    # but the generated ui files can be used at runtime by pyside.
    import os
    if not 'QT_API' in os.environ:
        os.environ.setdefault("QT_API", "PyQt")
    from PyQt4.QtGui import QIcon

    # TODO import you widget module
    from your_package.your_widget import QYourWidget

    # enumerates the widgets exposed by your plugins. If you don't do that, your
    # ui scripts won't load properly (you will have TypeError)
    PLUGINS_TYPES = {'QHomeWidget': pyqode.widgets.QHomeWidget}

    from pyqode.core.plugins.pyqode_core_plugin import CodeEditPlugin

    class YourPlugin(CodeEditPlugin):
        _module = 'your_package.your_widget' # path to the widget's module
        _class = 'QYourWidget'    # name of the widget class
        _name = "QYourWidget"  # I don't know why but this must be the same
                               # value as define for _class

        def createWidget(self, parent):
            return QYourWidget()


Now that you have a script you must install it as a **pyqode_plugins**. For that purpose
you must add an entry point to your setup.py:

.. code-block:: python

    setup(
        ...
        entry_points={'pyqode_plugins':
                     ['your_plugin_module = your_package.your_plugin_module']},
        ...
        )


.. _`pyqode.designer`: