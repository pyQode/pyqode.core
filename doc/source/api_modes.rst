Modes
=================
.. contents:: :local:

This page contains the documentation about the available modes. Most of them can
be used directly without any additional work while some others require
subclassing.

AutoIndentMode
-------------------

.. autoclass:: pyqode.core.AutoIndentMode
    :members:
    :private-members:

CaretLineHighlighterMode
------------------------------

.. autoclass:: pyqode.core.CaretLineHighlighterMode
    :members:

Code completion
-----------------

CodeCompletionMode
++++++++++++++++++++
.. autoclass:: pyqode.core.CodeCompletionMode
    :members:

CompletionProvider
++++++++++++++++++++++
.. autoclass:: pyqode.core.CompletionProvider
    :members:

Completion
++++++++++++++
.. autoclass:: pyqode.core.Completion
    :members:

DocumentWordCompletionProvider
+++++++++++++++++++++++++++++++++++
.. autoclass:: pyqode.core.DocumentWordCompletionProvider
    :members:

Code checkers
-------------------

CheckerMode
++++++++++++++++
.. autoclass:: pyqode.core.CheckerMode
    :members:

CheckerMessage
++++++++++++++++
.. autoclass:: pyqode.core.CheckerMessage
    :members:

Message status
+++++++++++++++++++++

.. autoattribute:: pyqode.core.MSG_STATUS_INFO

    Status value for an information message

.. autoattribute:: pyqode.core.MSG_STATUS_WARNING

    Status value for a warning message

.. autoattribute:: pyqode.core.MSG_STATUS_ERROR

    Status value for an error message

Check triggers
+++++++++++++++++++

.. autoattribute:: pyqode.core.CHECK_TRIGGER_TXT_CHANGED

    Check is triggered when text has changed

.. autoattribute:: pyqode.core.CHECK_TRIGGER_TXT_SAVED

    Check is triggered when text has been saved.
