What's New?
===========
This page lists the most prominent milestones achieved by the pyQode
developers. For more specific details about what is planned and what has been 
accomplished, please visit the `issues page on github`_ and the
:doc:`changelog </changelog>`, respectively.

Next Version
------------

We are working on a brand new major version of pyqode, version 2.0.

The next major version will focus on:
    - improving the subprocess server (1 per editor)
    - rewriting the code folder mode which is a mess at the moment
    - add multiple cursor support (if possible)
    - introduce smart completion (class, for loops, ...) such as in Eclipse or
      Visual C#

Milestones
----------

1.3.2
+++++

Fixed bugs:
    - server port was not forwarded by server.start
    - fix issue with file watcher if editor has been deleted.

1.3.1
+++++

Fixed bugs:
    - improve auto complete, many small bug fixes
    - fix infinite loop when saving an empty document
    - fix file watcher when filePath is None
    - fix a small bug with line panel where the last line was not
      highlighted as selected.

1.3.0
+++++
    - Add thread support to the subprocess server
    - Add to upper mode
    - Improve go to line dialog
    - Fix a few bugs with code completion and search and replace
    - Fix unicode error with python 2

1.2.0
+++++

Bug fixes release, no new features except for the debian packages available on
ppa:pyqode/stable.

1.1.0
+++++

    - Add AutoComplete mode
    - Add WordClickMode
    - Add Auto save on focus out setting
    - QT_API is now case insensitive
    - Improve inter-process communication speed and reliability

1.0.0
+++++


    - The API has been completely rewritten and renamed into pyQode.
    - It is now a namespace package; functionality are split over separate packages, pyqode.core being the foundation package.
    - It now supports both python 2.7 and python 3.3 and can works with PyQt4 or PySide.
    - The look and feel and the performances have been improved, the API is cleaner.
    - Qt designer plugins are also available.

0.2.0
+++++
    - Add python support:

        * code completion and calltips using `Jedi`_
        * inspection and code checking using pyflakes.py and pep8.py

0.1.0
+++++

    Initial development of PCEF with a focus on a generic code editor.


.. _`jedi`: https://github.com/davidhalter/jedi
.. _`issues page on github`: https://github.com/pyQode/pyqode.core/issues