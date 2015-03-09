Change Log
==========

2.5.0
-----

New features:
    - Unified API for document outline (see pyQode/pyQode#24)
    - Imrpove SlittableCodeWidget API: now an exception will be raised if the wrong type
      is passed to register_code_edit.

Fixed bugs:
    - InteractiveConsole: fix bugs which prevent from starting a new process (if another one is still running).


2.4.2
-----
New features:

- allow to reuse the same backend process for any new editor. This is not recommended but
  might be inevitable if you're running a proprietary python interpreter (see pyQode/pyQode#21)


Fixed bugs:

- fix auto-completion of backspace. Backspace should remove the corresponding character if next
  char is not empty and is in the mapping.  E.g.: (|), pressing delete at | should remove both parentheses
- fix show in explorer action (filesystem treeview) on Plasma 5
- fix cursor position after filewatcher reload (fix OpenCobolIDE/OpenCobolIDE#97)
- improve performances of OccurencesHighlighterMode
- fix a bug in auto-completion, mapping was not always respected and it sometimes happen
  that the closing symbol is not written if another closing symbol is after the text cursor.
- improve action "Duplicate line", now the entire selection will get duplicated (instead of the last line only).
- fix a bug with home key if the cursor is in the indentation are (first blank spaces).

2.4.1
-----

New features:

- FileWatcherMode: add file_reloaded signal to the


Fixed bugs:

- fix an issue with QTimer.singleShot
- fix encodings issue when pyqode is embedded into FreeCad (see pyQode/pyQode#11, end of topic)
- SplittableTabWidget: Fix issue when calling save and all editors has been closed
- SplittableTabWidget: Fix gui issue: panels of cloned editors should be hidden automatically
- FileSystemTree: fix issue when resetting path or when having two widget instances
- RecentFilesManager: fix duplicate entries on windows (see OpenCobolIDE/OpenCobolIDE#80
- FileWatcherMode: don't wait for the editor to get the focus to auto reload changed file

2.4.0
-----

New features:

- add a splittable tab widget
- add a file system tree view
- disable waiting cursor when waiting for code completions
- give more room to fold level value in block user state
- update qt and darcula pygments styles
- add support for pygments 2
- improvements to the syntax highlighter color scheme wrapper: more token types
  are available through the ``formats`` attribute.
- linter mode will use icon from theme on linux
- add more basic examples demonstrating the use of each mode/panel

Fixed bugs:

- many bug fixes and improvements to the indenter mode
- fix some bugs with pyside
- fix bugs with stange encoding names (pyQode/pyQode#11)
- fix a line ending issue with InteractiveConsole on windows (OpenCobolIDE/OpenCobolIDE#77)
- fix default font on OS X + PyQt4
- various non critical bug fixes in many modes/panels
- fix a performance critical issue with code completion model updates: it will
  now update 100 times faster and will never block the ui even when working with
  big files (where there is more than 5000 completions items).

Deprecated features:

- pyqode.core.widgets.TabWidget is deprecated and will be removed in version
  2.6
- backend: there is no more boolean status returned by the backend, you should
  adapt both your caller and callee code.

Removed features (that were deprecated since at least 2.2.0):

- pyqode.core.qt has been removed. You should now use pyqode.qt.

2.3.2
-----

Fixed bugs:

- fix occasional crash when closing an editor
- fix restore cursor position: center cursor
- fix useless calls to rehighlight

2.3.1
-----

Fixed bugs:

- Fix segfault on windows

2.3.0
-----

New features:

- add support for python2. You may now use python2 for writing a pyqode
  app (backend AND frontend)!
- add a mode that highlight occurrences of the word under the text cursor
- add a smart backspace mode, this mode eats as much whitespace as possible
  when you press backspace
- add GlobalCheckerPanel that shows all errors found in the document
- add extented selection mode. Extended selection is a feature that can be
  found in Ulipad ( https://code.google.com/p/ulipad )
- add pyqode-console script that let you run other programs in an external
  terminal with a final prompt that holds the window after the program
  finished.
- new widget: prompt line edit (a line edit with a prompt text and an icon)
- add ability to surround selected text with quotes or parentheses
- search and replace: added regex support
- search and replace: the search algorithm is now running on the backend
  (fix issue where gui was blocked while searching text)
- improvements to the InteractiveConsole: there is now a way to setup
  colors using a pygments color scheme. Also the console is now readonly
  when the process is not running
- backend improvements:
- the backend is now a ThreadedSocketServer
- proper way to close the backend process. we do not use terminate/kill
  anymore but send a shutdown signal to the process stdin


Fixed bugs:

- fix the code that prevents code completion popup from showing in strings
  and comments
- fix a bug with the default indenter that was eating chars at the start
  of the line
- fix checker request logic (keep the last request instead of the first
  one)
- fix right panels top position
- fix wordclick decoration color on dark color schemes


2.2.0
-----

New features:
    - add cursor position caching
    - add ``updated`` signal to RecentFilesManager
    - add ability to add menus to the editor context menu
    - add get_context_menu method to CodeEdit
    - add ``is_running`` property to InteractiveConsole
    - add ``double_clicked`` signal to TabWidget
    - add a way to override folding panel indicators and background color
    - add a way to pass an icon provider to the RecentMenu
    - added a small delay before showing fold scopes (to avoid flashes when
      you move the mouse over the folding panel)
    - add a way to make the distinction between default font size and zoomed
      font size by introducing the notion of zoom level
    - a few more improvements to the completion popup (it should hide
      automatically when you move the cursor out of the word boundaries)

Fixed bugs:
    - fix confusing convention: now both line numbers and column numbers starts
      from 0
    - fix a few issues with code folding (corner cases such as indicator on
      first line not highlighted,...)
    - fix potential circular import with the cache module
    - fix caret line refresh when dynamically disabled/enabled
    - fix a visual bug where horizontal scroll-bars range is not correct
    - fix tooltip of folded block: ensure the block is still folded before
      showing the tooltip
    - fix background color when a stylesheet is used (especially when
      stylesheet is reset).

2.1.0
-----

New features:
   - new code folding API and panel
   - encodings API (panel, combo box, menu, dialog)
   - allow to use pygments styles for native highlighters
   - improved checker mode and syntax highlighter
   - new CheckerPanel made to draw the new checker mode messages. If you were
     using MarkerPanel to draw checker messages, you will have to replace it by
     CheckerPanel!
   - mimetype property for CodeEdit
   - optimized API for storing block user data (using a bitmask in block user
     state)
   - reworked editor context menu (add a way to add sub-menus)
   - improved code completion: show popup when typing inside an existing word
     and always collect completions at the start of the prefix (this gives a
     lot more suggestions).
   - add pre-made editors: TextCodeEdit and GenericCodeEdit

Fixed bugs:
    - wrong cursor position after duplicate line
    - empty save dialog for new files (without path)
    - fix style issue on KDE
    - fix some issues with frozen applications
    - fix a few bugs in the notepad example
    - fix a long standing issue in symbol matcher where the mode would
      match symbols that are inside string literals or comments. This greatly
      improves the python auto indent mode.

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
 * auto indent mode(indentation level
