Getting started
===============

This page is a gentle introduction to the pyQode framework.

Before reading this, you should have ``pyqode.core`` and ``PySide/PyQt4/PyQt5``
:doc:`installed </download>` on your system.

Design and philosophy
---------------------

In opposition to what other code editor projects might do, pyqode does not aim to support all
languages from scratch. Instead it provides a framework that let you build the code editor
of your dream for your favorite language. pyqode.core really is a toolbox that you will use to build
your own specialised code editor.

A generic code editor exists in pyqode.core but it is highly inefficient and
probably not good enough to target your preferred language. It is there to be used as a fallback
editor for secondary languages (i.e. languages that are not the main target of
your application, for whatever reason).

There are many reasons why you would want to build a specialised editor instead of using
:class:`pyqode.core.widgets.GenericCodeEdit`. We can see the following reasons:

    - implement a native highlighter for maximum flexiblity and better load times (the generic
      pygments highlighter is usually 2-3 times slower than a native one).
    - implement code folding. Code outline must be detected differently depending on the language. That's
      why the generic pygments highlighter does not detect code outline at all.
    - implement a code completion engine. Not every language use the same tools, you will be better
      served by a specialised completione engine than by trying to use a generic one.


Support for new languages are added by external (namespace) packages. That way, the user can only pick
up what he needs, minimizing the list of dependencies. If you are working on Go editor, you would not want
to have to download clang, jedi or pyFlakes. The only dependency you will have are the pyqode.core dependencies
which boil down to pygments and optionally chardet.

Packages
--------

Here is a brief overview of the content of pyqode.core and how to import it.

pyqode.core is made up of a series of subpackages. Each subpackage defines its
own api (classes defined in a module of a subpackage are available at the
subpackage level).

Here are the main subpackages:

    - api: contains the bases classes of the API
    - backend: classes for controlling the backend process
    - modes: contains all available modes
    - panels: contains all available panels
    - styles: contains a series of pygments styles specific to pyQode
    - widgets: contains a series of useful widgets.

.. note:: Not all subpackages are presented here, internal package or very
          specific one have been left out. You can read more about them in the
          API reference section.

To use pyQode, simply import one of those packages::

    from pyqode.core import api
    from pyqode.core import backend
    from pyqode.core import modes
    from pyqode.core import panels
    from pyqode.core import widgets

    # then you start using pyqode, e.g:
    editor = api.CodeEdit()
    editor.modes.append(modes.CodeCompletionMode())
    editor.panels.append(panels.LineNumberPanel())

    tabWidget = widgets.TabWidget()
    tabWidget.add_code_edit(editor)


Selecting a Qt bindings
-----------------------

The first thing to do when using pyQode is to specify the Qt bindings you want
to use in your application.

By default, pyQode will try to use PyQt5 and will fallback to PyQt4 or PySide in
case of import errors. You can enforce the use of a specific bindings by
setting up the ``QT_API`` environment variable.

For example, to use PySide::

    import os
    os.environ['QT_API'] = 'PySide'
    from pyqode.core.qt import QtCore, QtGui, QtWidgets
    print('Qt version:%s' % QtCore.__version__)
    print(QtCore.QEvent)
    print(QtGui.QPainter)
    print(QtWidgets.QWidget)


.. note:: You can also use the qt package of pyqode.core to write a bindings
          independent application but you have to be aware that
          ``pyqode.core.qt`` does not wrap the entire Qt API (it only what was
          required to write pyQode).

The backend
-----------

pyQode is a client server API, the GUI side is called the ``frontend`` and
the background process used to perfom heavyweight computation is called the
``backend``.

When writing a pyQode application, you have to write both the frontend script
and the backend script. Fortunately, writing the backend script is an easy
task. All you have to do is to configure the server script
(sys.path, workers,...) and call :meth:`pyqode.core.backend.serve_forever`

Here is an example of server script::

    from pyqode.core import backend

    if __name__ == '__main__':
        backend.CodeCompletionWorker.providers.append(
            backend.DocumentWordsProvider())
        backend.serve_forever()


The frontend
------------

Writing the pyqode frontend is not more complicated than writing the backend.

All you have to do is:

    1) create a :class:`pyqode.core.api.CodeEdit`
    2) start the backend process
    3) configure CodeEdit
    4) open a file or set some text
    5) run the Qt main loop

Here is a simple example of a frontend script::

    import sys
    from pyqode.core import api
    from pyqode.core import modes
    from pyqode.core import panels
    from pyqode.core.qt import QtWidgets


    if __name__ == "__main__":
        app = QtWidgets.QApplication(sys.argv)

        # create editor and window
        window = QtWidgets.QMainWindow()
        editor = api.CodeEdit()
        window.setCentralWidget(editor)

        # start the backend as soon as possible
        editor.backend.start('server.py')

        # append some modes and panels
        editor.modes.append(modes.CodeCompletionMode())
        editor.modes.append(modes.PygmentsSyntaxHighlighter(editor.document()))
        editor.modes.append(modes.CaretLineHighlighterMode())
        editor.panels.append(panels.SearchAndReplacePanel(),
                          api.Panel.Position.BOTTOM)

        # open a file
        editor.file.open(__file__)

        # run
        window.show()
        app.exec_()

CodeEdit
--------

The editor widget is a simple extension to QPlainTextEdit.

It adds a few utility signals/methods and introduces the concept of
**Managers, Modes and Panels**.

A **mode/panel** is an editor extension that, once added to a CodeEdit
instance, may modify its behaviour and appearance:

  * **Modes** are simple objects which connect to the editor signals to append new behaviours (such as automatic indentation, code completion, syntax checking,...)

  * **Panels** are the combination of a **Mode** and a **QWidget**. They are
    displayed in the QCodeEdit's content margins.

    When you install a Panel on a CodeEdit, you can choose to install it in
    one of the four following zones:

        .. image:: _static/editor_widget.png
            :align: center
            :width: 600
            :height: 450

A **manager** is an object that literally manage a specific aspect of
:class:`pyqode.core.api.CodeEdit`. There are managers to manage the list of
modes/panels, to open/save file and to control the backend:

    - :attr:`pyqode.core.api.CodeEdit.file`:
        File manager. Use it to open/save files or access the opened file attribute.
    - :attr:`pyqode.core.api.CodeEdit.backend`:
        Backend manager. Use it to start/stop the backend or send a work request.
    - :attr:`pyqode.core.api.CodeEdit.modes`:
        Modes manager. Use it to append/remove modes on the editor.
    - :attr:`pyqode.core.api.CodeEdit.panels`:
        Modes manager. Use it to append/remove panels on the editor.

Starting from version 2.1, CodeEdit defines the :attr:`pyqode.core.api.CodeEdit.mimetypes` class attribute.
property which is a list of supported mimetypes. An empty list means the CodeEdit is generic.
**Code edit specialised for a specific language should define this attribute!**

IDE can use that property and and :meth:`mimetypes.guess_type` to make file types-editor associations.

Controlling the backend
-----------------------

To use the backend (from the frontend), you need to use :class:`pyqode.core.managers.BackendManager`.

To start the backend, use :class:`pyqode.core.managers.BackendManager.start`.
You can specify a custom interpreter if needed (useful in python for
working with a python2 interpreter or when using a virtual environment)::

    code_editor.backend.start('path/to/server_script.py',
                              interpreter='/usr/bin/python2.7')


To request some work to be done on the backend, just use :class:`pyqode.core.managers.BackendManager.send_request`.
You can specify a callback to be called when the work has finished (i.e. to
retrieve the job results)::

    code_editor.backend.send_request(my_worker, {'parameters': None,}, my_callback)


To stop the backend, just use :class:`pyqode.core.managers.BackendManager.stop`::

    code_editor.backend.stop()

You should not need to call it manually as the backend is automatically stopped
when the editor got deleted by the python interpreter.

Opening and saving files
------------------------

Opening and saving files is made easy by using the
:class:`pyqode.core.managers.FileManager`.

Opening a file::

    code_edit.file.open('/path/to/file.py')

Saving a file::

    code_editor.file.save()

Saving a file as::

    code_editor.file.save('/path/to/new_file.py')

You can always replace a manager by your own version if you're not happy with it
or if you want to extend it.


Using modes and panels
----------------------

To use modes and panels, you must use the corresponding managers:

    - :class:`pyqode.core.managers.ModesManager` for modes
    - :class:`pyqode.core.managers.PanelsManager` for panels

Those managers are available as attributes of CodeEdit:

    - :attr:`pyqode.core.api.CodeEdit.modes`
    - :attr:`pyqode.core.api.CodeEdit.panels`

To install a mode/panel, use the ``append`` method::

    code_editor.modes.append(MyMode())

To retrieve a mode/panel, use the ``get`` method. This method accepts either the
mode name or the mode class::

    m_name = code_editor.modes.get('MyMode')
    m_class = code_editor.modes.get(MyMode)
    assert m_name == m_class

.. note:: The order of installation of modes is important because some modes
    have interdependances. Also it is worth noting that the order of
    installation of modes define the order of reaction to a specific events.

    Usually, this kind of restriction is documented for a specific modes in its
    class documentation.

Changing editor style and properties
------------------------------------

You can change any property of CodeEdit, or any of its modes, at runtime.

E.g.::

    # change color scheme
    code_editor.modes.get(PygmentsSyntaxHighlighter).pygments_style = 'monokai'
    # change property
    code_editor.show_white_spaces = True
    # change action shortcut
    code_editor.action_duplicate_line.setShortcut('Ctrl+Shift+Down')
