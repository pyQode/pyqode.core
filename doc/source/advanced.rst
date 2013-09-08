Advanced topics
==================

This page covers advanced topics

.. contents:: :local:

Styling
----------

You can easily create new styles by subclassing :class:`pcef.style.Style` or by creating a JSON file with the following
structure::

    {
        "marginColor": "#FF0000",
        "searchBackgroundColor": "#FFFF00",
        "fontName": "monospace",
        "selectionBackgroundColor": "#6182F3",
        "name": "YourStyleName",
        "searchColor": "#000000",
        "pygmentsStyle": "friendly",
        "panelSeparatorColor": "#cccccc",
        "selectionTextColor": "#ffffff",
        "fontSize": 10,
        "showWhitespaces": true,
        "lineNbrColor": "#808080",
        "activeLineColor": "#E4EDF8",
        "panelsBackgroundColor": "#dddddd",
        "marginPos": 80
    }

You can change the editor style by setting the currentStyle property but you should also add it to the styles package

.. code-block:: python

    style = pcef.style.fromJSON("style.json")
    # add it to the styles dictionary so that it can be retrieved easily for a later use
    pcef.styles.addStyle(style)
    # set our editor style
    editor.currentStyle = style


Here is how you can retrieve a built-in style (or a style you added using addStyle)

.. code-block:: python

    from pyqode.styles import getStyle
    defaultStyle = getStyle('Default')
    darkStyle = getStyle('Dark')

.. note:: There is two built-in styles immediately available: **Default** and **Dark**.

.. warning:: The pygmentsStyle setting must be a valid pygments style name.

Creating custom modes and panels
----------------------------------

To create a custom mode or Panel you should first inherit :class: `pcef.core.Mode` or :class: `pcef.core.Panel` as shown
in the following example:


.. code-block:: python

    from pyqode.core import Mode
    from pyqode.core import Panel

    class MyMode(Mode):

        def __init__(self):
            super(MyMode, self).__init__("My mode", "An example of custom mode")

        def _onStyleChanged(self):
            pass  # overrides this if you need to update colors, brushes, ...

        def _onStateChanged(self, state):
            if state is True:
                pass  # connect to self.editor.textEdit events
            else:
                pass  # disconnect from self.editor.textEdit events

    class MyPanel(Panel):

        def __init__(self):
            super(MyPanel, self).__init__("My Panel", "An example of custom Panel")

        def _onStyleChanged(self):
            pass  # overrides this if you need to update colors, brushes, ...

        def _onStateChanged(self, state):
            if state is True:
                pass  # connect to self.editor.textEdit events
            else:
                pass  # disconnect from self.editor.textEdit events