Advanced topics
==================

This page covers advanced topics:

.. contents:: :local:

Styling
----------

pyQode use the PropertyRegistry class to store style and settings properties.
A property registry is a simple **dictionary of properties** (key/values)
organised per section. It can be easily serialised to **JSON**.

QCodeEdit defines a series of style/settings properties in the "General"
section. Modes and panels are also free to add their properties when they are
installed on an editor instance. This means that you'll end up with completely
different dictionaries depending on the installed mode.

For example, consider the difference between the QCodeEdit and the
QGenericCodeEdit settings:

    * QCodeEdit:
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
          you can always dumps the style and settings dictionaries to a JSON
          string::

            print(editor.settings.dump())
            print(editor.style.dump())

          You can also find the list of style/settings properties that a
          specific mode/panel adds to the editor by consulting the API reference
          related to that specific mode/panel.

          *Every Mode/Panel should have a table that list those properties along with the section they belong to.
          If the mode/panel does not add any properties, it should clearly indicate it. If this is not the case, report it on the github bug tracker.*

Changing a property manually:
+++++++++++++++++++++++++++++++++++++++++++

You can change the style and settings values using the style and settings
properties of QCodeEdit:

.. code-block:: python

    editor.style.setValue("background", QColor("#FF5436"))
    editor.settings.setValue("showWhiteSpaces", True))

When you change a value, a signal is emitted so that the concerned modes/panels
can adapt their brushes, pens, stylesheets,... This is important to consider
when making new modes/panels that depend on such properties.

Save/Load from file:
+++++++++++++++++++++++++++++++++++++++++++

Style and settings can be serialized to JSON easily:

.. code-block:: python

    # Editor 01: modify default style to be dark then save it to "dark.json"
    file_path = "dark.json"
    editor_01 = pyqode.core.QCodeEdit()
    editor_01.style.setValue("background", "#222222")
    editor_01.style.setValue("foreground", "#888888")
    editor_01.style.save(file_path)

    # Editor 02: style loaded from the file we just saved
    editor_02 = pyqode.core.QCodeEdit()
    editor_02.style.open(file_path)
    editor_02.show()


Creating modes and panels
-------------------------------------

pyQode tends to prefer composition over inheritance, that why should plan to
create a new mode/panel whenever you want to extends the functionality of
QCodeEdit.

You do that by subclassing **pyqode.core.Mode** or **pyqode.core.Panel**.
Creating a mode or a panel is mostly the same.

When you create a new mode you must give him an IDENTIFIER and a DESCRIPTION::

    class MyMode(Mode):
        IDENTIFIER = "myMode"
        DESCRIPTION = "An example mode"

The IDENTIFIER string is set as the mode name and is used to identify the mode
when installed on a QCodeEdit. It is also the attribute name you can use to get
back a reference on the mode::

    editor.installMode(MyMode())
    print(editor.myMode)

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

     This method is called when the mode is installed on a QCodeEdit.

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
            pass  # you can update some style options here

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
            pass  # you can update some style options here


Code checker modes
++++++++++++++++++++++

pyQode have a base mode to help you write code checker modes: pyqode.core.CheckerMode

To create a new checker mode, you can simply subclass CheckerMode and pass him
the checker function that needs to be executed contextually. The CheckerMode will
actually execute this function in a background process. It will collect the
results/messages you append to the Queue.

Here is a typical implementation of a new checker mode:

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

.. note:: Checker request are configurable:

            * **pyqode.core.CHECK_TRIGGER_TXT_CHANGED**: the checker function will run every time the text changed and the user is idle (i.e. not typing some text)

            * **pyqode.core.CHECK_TRIGGER_TXT_SAVED**: the checker function will only run when the user save the editor's content.

Code completion modes
++++++++++++++++++++++


Syntax highlighter modes
+++++++++++++++++++++++++


Code folding modes
+++++++++++++++++++++++++


Designer plugins
--------------------
