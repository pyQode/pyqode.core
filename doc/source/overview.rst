Overview
*******************

An easy to use and easy to customise full featured **code editor** for any
**PySide** based applications.


Features:
===============

*(+): implemented, (-): not implemented*

Generic (language independent):
    * (+) **syntax highlighting** using pygments
    * (-) **code completion** (document based, list based or custom)
    * (+) **unicode** support (specify encoding when you load your file)
    * (+) **line number**
    * (+) **margin markers**
    * (+) **right margin**
    * (+) **active line highlighting**
    * (-) **code folding**
    * (+) **text decorations** (squiggle, box)
    * (+) **flexible framework** to add custom widgets or specific behaviour

Python specific:
    * (-) python **smart indentation**
    * (-) python **code completion** using *rope*
    * (-) python **refactoring** using *rope*
    * (-) python **pep8 checking**  (pep8.py is run on the fly)
    * (-) python **syntax checking** using PyFlakes


Design
====================

The widget is designed as a super widget that contains a specialised text edit
and a series of panels drawn around the text edit.

User can add specific behaviours by installing modes.


CodeEditor widget (QCodeEditor)
-----------------------------------------------------------

This is the main widget for the end user. It contains the QCodeEdit widget, a
series of zones where custom widgets can be added.

It provides all the methods to manage panels, modes and text edit style,
settings and decorations.


CodeEdit widget (QCodeEdit)
--------------------------------------------------------------

A specialised QTextEdit that provides text manipulation functionnalities (
indenting text, adding text decorations, provides additional signals).

Note: it does not perform syntax highlighting or code completion explicitly.
Those features are performed by modes.


Panels widgets (QEditorPanel)
-------------------------------------------------------------

Panels are used to draw specific/custom widgets around the text edit (line
number panel, markers panels (breakpoints, folding,...), code browser, ...).

Panels are placed in one of the 4 following zones:
    * **ZONE_TOP** (vertical layout)
    * **ZONE_BOTTOM** (vertical layout)
    * **ZONE_LEFT** (horizontal layout)
    * **ZONE_RIGHT** (horizontal layout)

Panels are managed by the editor widget itself. The widget provides methods to
add, remove, move, hide/show panels.

Builtin panels:
    * (+) **LineNumberPanel**
    * (-) **FoldingPanel**
    * (-) **MarkerPanel**
    * (-) **SearchAndReplacePanel**
    * (-) **PythonBrowserPanel**


Modes (Mode)
----------------

User can customize the editor behaviour (e.g. add specific features such as
code syntax checking,...) by installing modes.

Modes are simple object that get a reference to the editor widget in order to
perform a specific/custom action on the editor text edit or on one of its
panels. Modes are managed from the editor widget itself. The widget provides
methods to add, remove, enable/disable or get a specific mode. Modes are
identified by a unique string identifier.

Builtin modes:
    * (+) **SyntaxHighlighting**
    * (+) **RightMargin**
    * (+) **ActiveLineHighlight**
    * (-) **HighlightOccurrences**
    * (-) **CodeCompletion**
    * (-) **Pep8Checker**
    * (-) **PySyntaxChecker**
    * (-) **PySmartIndenter**
    * (-) **PyRefactor**
    * (-) **PyExecuteFile**

User can enable/disable a specific mode.
User can add its own modes by calling the installMode method with a subclass of
Mode.