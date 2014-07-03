Change Log
==========

.. note::

    These lists are not exhaustive.

2.0.0
-----

New features/improvements:
    - PyQt5 support
    - Mac OSX support
    - new client/server API
    - simpler settings API
    - simpler modes/panels API
    - there is now a way to select the python interpreter used for the backend
      process
    - integrate widgets defined in pyqode.widgets (pyqode.widgets will be
      removed soon)
    - allow tab key to choose a completion
    - new pyqode specific pygments color schemes

Fixed bugs:
    - fix zombie backend process
    - fix unsupported pickle protocol
    - fix list of pygments style: all styles are now included, including plugins!

1.3.2
-----

Fixed bugs:
    - server port was not forwarded by server.start
    - fix issue with file watcher if editor has been deleted.

1.3.1
-----

Fixed bugs:
    - improve auto complete, many small bug fixes
    - fix infinite loop when saving an empty document
    - fix file watcher when filePath is None
    - fix a small bug with line panel where the last line was not
      highlighted as selected.

1.3.0
-----

New features:

    - case converter mode
    - improve go to line dialog


Fixed bugs:

    - fix bugs with replace all
    - Fix wrong behavious with auto completion
    - Fix a bug where it was not possible to select a code completion using ENTER
    - fix UnicodeEncodeError with python 2.7

1.2.0
-----

New features:
    - debian packages available on ppa:pyqode/stable and ppa:pyqode/unstable

Fixed bugs:

    - Code Completion does not trigger if there is a string or comment in the line
    - Fix filewatcher bug with deleted files
    - Fix filewatcher bug when user say no to file reload the first time
    - Fix syntax highlighter bugs with old PyQt libraries.


1.1.0
-----

New features:

  - Improve code completion process performances and reliability
  - Make QT_API case insensitive
  - Wrap settings and style properties with python properties
  - Allow user to start code completion server before a code editor instance is created.
  - New mode: AutoComplete mode
  - New mode: WordClickMode, append support for word under MOUSE cursor
  - New setting: autoSave on focus out

Fixed bugs:

  - Fix bug with subprocess intercomm (and improves performances)
  - Fix Document cleanup bugs


1.0.0
-----

The API has been completely rewritten. Here are the major changes

 * added support for python 3
 * added support for PyQt5
 * added support for Qt Designer plugins
 * morphed into a namespaces package
 * improved look and feel: native look and feel close to Qt Create
 * improved code completion, code folding,
 * improved performances (using multiprocessing heavily instead of multithreading)
 * complete documentation and examples
 * minimum travis ci integration (just to ensure pyqode remains importable for all supported interpreter/qt bingins, there is still no real test suite).

0.1.1
-----

Fixed bugs:
    - better code completion popup show/hide


0.1.0
-----

First release. Brings the following features:

 * syntax highlighting mode (using pygments)
 * code completion (static word list, from document words)
 * line number Panel
 * code folding Panel
 * markers Panel (to append breakpoints, bookmarks, errors,...)
 * right margin indicator mode
 * active line highlighting mode
 * editor zoom mode
 * find and replace Panel
 * text decorations (squiggle, box)
 * unicode support (specify encoding when you load your file)
 * styling (built-in white and dark styles + possibility to customize)
 * flexible framework to append custom panels/modes
 * auto indent mode(indentation level is based on the previous line indent)