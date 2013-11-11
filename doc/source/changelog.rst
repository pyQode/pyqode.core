Change Log
===========

.. note::

    These lists are not exhaustive.

1.1
---------

New features:

  - Improve code completion process performances and reliability
  - Make QT_API case insensitive
  - Wrap settings and style properties with python properties
  - Allow user to start code completion server before a code editor instance is created.
  - New mode: AutoComplete mode
  - New mode: WordClickMode, add support for word under MOUSE cursor
  - New setting: autoSave on focus out

Bug fixed:

  - Fix bug with subprocess intercomm (and improves performances)
  - Fix Document cleanup bugs


1.0
----------

The API has been completely rewritten. Here are the major changes

 * added support for python 3
 * added support for PyQt4
 * added support for Qt Designer plugins
 * morphed into a namespaces package
 * improved look and feel: native look and feel close to Qt Create
 * improved code completion, code folding,
 * improved performances (using multiprocessing heavily instead of multithreading)
 * complete documentation and examples
 * minimum travis ci integration (just to ensure pyqode remains importable for all supported interpreter/qt bingins, there is still no real test suite).

0.1.1
----------

Bug fixes release:
    - better code completion popup show/hide


0.1.0
-------

First release. Brings the following features:

 * syntax highlighting mode (using pygments)
 * code completion (static word list, from document words)
 * line number Panel
 * code folding Panel
 * markers Panel (to add breakpoints, bookmarks, errors,...)
 * right margin indicator mode
 * active line highlighting mode
 * editor zoom mode
 * find and replace Panel
 * text decorations (squiggle, box)
 * unicode support (specify encoding when you load your file)
 * styling (built-in white and dark styles + possibility to customize)
 * flexible framework to add custom panels/modes
 * auto indent mode(indentation level is based on the previous line indent)