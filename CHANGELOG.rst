Change Log
==========

2.11.0
------

As of pyqode 2.11, the project has entered in maintainance mode. Only critical bug fixes will be adressed. The core
team won't add any new features but we will continue to accept PR as long as they are properly tested and not too risky.

This release is mainly a bug fix release, it also adds support for PyQt 5.7.

New features:

- PyQt 5.7 support
- Allow to set case sensitiveness of current word highlighter

Fixed bugs:

- Fix compatibility issues with PyQt 5.7
- JSonTcpClient: wait for socket connected on OSX
- Fix FileNotFoundError in file watcher
- SplittableTabWidget display file save exception in a message box
- Many bug fixes to the new OutputWindow/Terminal widget
- Fix OpenCobolIDE/OpenCobolIDE#365
- Fix OpenCobolIDE/OpenCobolIDE#376
- Fix OpenCobolIDE/OpenCobolIDE#377
- Fix pyQode/pyQode#69
- Fix pyQode/pyQode#67
- CodeCompletion: fix regex exception when setting prefix

2.10.1
------

Fixed bugs:

- fix some backend issues on OSX (the client socket would remain in conecting state if a request is made before
  the tcp server is running)
- fix strange behaviour in buffered input handler of OutputWindow when using backspace or delete

2.10.0
------

New features:

- add a new widget to run interactive process with support for ANSI Escape Codes: pyqode.core.widgets.OutputWindow
- add a Terminal widget based on the new OutputWindow.
- [CodeCompletionMode] improvements to the subsequence matching algorithm to put completion with the same case at the top of the list.
- [SplittableTabWidget] add shortcuts to close current tab (Ctrl+W) or all tabs (Ctrl+Shift+W)

Fixed bugs:

- [FSTreeView] fix file_renamed signal not emitted when moving files
- [FSTreeView] show a message box if there is an OSError while renaming a file/directory

Deprecated features:

- pyqode.core.widgets.InteractiveConsole is now deprecated, you should use pyqode.core.widgets.OutputWindow

2.9.0
-----

New features:

- add ability to extract translatable strings with gettext
- add an option to disable copy of whole line when there is no selection, see PR #158
- add a public method to retrieve the list of submenu of the editor context menu
- add ``keys`` and ``values`` methods to the mode and panel manager
- FSTreeView: delay initialisation of tree view until widget is shown
- Add zoom menu to the editor's context menu
- Add ability to use own QSettings
- Add ability to set custom linter rules and add an option for the backend to know about max_line_length (defined in
  the margin mode).
- Add ability to close tabs on the left/right of the current tab.

Fixed bugs:

- fix conflicts between WordClickMode and Ctrl+Mouse move (prevent goto when Ctrl+ mouse move).
- fix text cursor not visible under a margin (solution is to use a 2px wide cursor).
- fix HackEdit/hackedit#51
- fix cut not working as intended when cutting a line with only whitespaces
- fix memory issues in HtmlPreviewWidget, now using QTextEdit::setHtml instead of a full blown webview
- fix subprocess.CalledError if xdg-mime returns with non-zero exit code
- fix segfault on Windows (in HackEdit)
- fix many potential unhandled OSError/subprocess errors
- fix file_renamed signal not emitted for child file when a parent directory has been renamed (FSTreeView)
- fix KeyError in backend client if backend function failed due to an exception (result is None)
- fix UnicodeDecodeError when decoding stdout/stderr in InteractiveConsole
- fix backend output not shown in logs when running from a frozen application
- fix mode enabled on install even if enabled was set to False in the constructor
- fix extra selection spanning over multiple lines when user inserts a line breaks (CheckerMode)
- restore case insensitive code completion by default which was causing some major issues in OpenCobolIDE
- fix ImportError when looking for a pygments lexer (and the application has been freezed without all possible
  pygments lexers)


2.8.0
-----

New features:

- new pyqode package: pyqode.rst (ReStructuredText)
- enable case sensitive code completion by default
- add a new widget: HtmlPreviewWidget. This widget display the preview of an
  editor that implement the ``to_html`` method. (use for the new pyqode
  package: pyqode.rst)
- enable code completion in strings (it's up to the cc engine to treat them
  differently)
- SplittableCodeEditTabWidget: add a way to repen recently closed tabs
- CI improvements: tests are now running with both PyQt4 and PyQt5 on Travis CI

Fixed bugs:

- fix PYGMENTS_STYLES not including our own styles if pyqode not in standard path (OCIDE now bundles pyqode)
- fix wrong modifiers used for indent/unindent: Ctrl+Tab and Ctrl+Shift+Tab can
  now be used to cycle through the tabs of a QTabWidget
- fix AttributeError in FSTreeView: msg box does not have an error method,
  use critical instead
- fix unable to create directories/files that starts with '.' in FSTreeView (hidden on linux)
- fix AttributeError in splittable tab widget if editor widget is not a CodeEdit
- fix AttributeError: 'NoneType' object has no attribute 'state' in InteractiveConsole
- fix some segmentation faults when using PyQt4
- fix highlighting not working in split editor if original editor has been
  closed.
- fix a memory leak in the backend manager
- fix unreadable search occurences if foreground color is white (dark themes)
- fix wrong tag color in QtStyle pygments style
- fix AttributeError: 'NoneType' object has no attribute '_port' in BackendManager


2.7.0
-----

New features:

- Add a panel to indicate when a file is read-only. The panel will disappear
  as soon as the file becomes writeable.
- Add a new mode that remember the cursor history (you can go back and go
  forward the cursor history by using Ctrl+Alt+Z and Ctrl+AltY)
- Add a new mode that can highlight a specific line of code (could be used
  in a debugger plugin to indicate the line where the debugger has been
  stopped...)
- SplittableTabWidget: add "Detach tab" option in the context menu.
- SplittableTabWidget: add a signal for when the editor has been created
  but the file has not been loaded yet
- SplittableTabWidget: add a signal for when the editor has been created
  and the file has been loaded
- SplittableTabWidget: add a signal for when the editor content has been
  saved to disk
- Improve MarkerPanel to be used for a breakpoints panel: add
  edit_marker_requested signal and improve internals
- InteractiveConsole: add the SearchPanel to the console so that you
  can easily search for a word in the process' output
- FileSystemTreeView: add ability to set a custom file explorer command
- CodeEdit: Reoganisation of the context menu. By default all new actions
  (that are not part of QPlainTextEdit) will go to an 'Advanced' sub-menu.
  You can also specify a custom sub-menu name or None. All languages
  specific extensions (pyqode.python,...) will use a menu with the name
  of the language (e.g. Python->Goto definition,
  COBOL->Compute field offsets, ...)
- CodeCompletionMode: add support for MatchContains if using PyQt5
- pyqode.core.share.Definition: add path attribute
- Backend: add a heartbeat signal. If no signal was received for
  a certain duration, the backend process will exit. This fix an issue
  where the backend process were still running as zombies when the parent
  crashed.
- SearchPanel: allow to search backward with Shift+Enter when the focus is
  in the search box
- SearchPanel: add ability to search in the selected text only.
- The document outline tree widget is now able to sync with the editor
- Add two new logging levels: 1 = debug communication, 5 = internal debugging

Fixed bugs:

- CodeEdit: Fix panel margins not refreshed if panel.setVisible has been called
  before the editor is visible.
- SplittableTabWidget: Fix save as not working anymore
- InteractiveConsole: make console read only when process has finished.
- DarculaStyle: fix diff tokens color
- Fix a few TypeError with PyQt 5.5.x
- Fix laggy SearchPanel panel if use enter a space character.
- Fix an encoding issue on Windows in the client-process communication
- ErrorTable: Fix newlines not visible in details dialog.
- Fix many potential memory leaks by breaking the circular dependencies
  correctly before removing a mode/panel
- Improve Cache.get_encoding: it will try all preferred encoding if the file
  is not in the cache before giving up.
- SplittableTabWidget: Normalize case of input file paths when looking if The
  file is already open. Since Windows is not case sensitive, the file might be
  already opened but with a different case...
- TextBlockHelper: fix TypeError on some 32 bits systems with old Qt5 libraries

2.6.9
-----

Fixed bugs:

- fix UnicodeDecodeError with the backend process
- fix cursor selection lost after a case conversion
- fix context menu entries not working at mouse position


2.6.8
-----

Fixed bugs:

- fix a few more type errors when using PyQt5.5
- fix runtime error in outline mode if the editor has been deleted before
  the timer elapsed.

2.6.7
-----

Fixed bugs:

- fix TypeError in FileSystemHelper with PyQt5.5
- fix blank file icons with PyQt5.5

2.6.6
-----

Fixed bugs:
    - FSTreeView: fix bug with cut of directories
    - SplittableCodeEditTabWidget: fix keep unique tab text on save
    - FileManager: fix bug in clean text when text is empty
    - FileManager: fix log level of unwanted/parasiting info messages
    - FileManager: don't save file if editor is not dirty and encoding has not changed
    - Folding: fix issue with deleting folded scope.

2.6.5
-----

SplittableTabWidget: Fix save_as not using all mimetypes extensions.

2.6.4
-----

Fixed bugs:
    - fix panels margins not refreshed if panel.setVisible has been called while the editor widget was not visible.
    - fix bug with filewatcher on file deleted if the user choose to keep the editor open

2.6.3
-----

Improvements:
    - a few improvements to some internal functions which leads to better
      performances in big files.
    - add file_size_limit to FileManager, when the file size is bigger than the
      limit, syntax highligher will get disabled
    - Improve plasma 5 integration (will use more icons from theme (
      code-variable, code-function,...))
    - Simplified color_scheme api, SyntaxHighlighter.color_scheme now accepts
      a string instead of a ColorScheme instance

Fixed bugs:
    - Fix Ctrl+Home (jump to first line)
    - Fix copy of directory in FileSystemTreeView
    - Fix file watcher notification when saving big files.


2.6.2
-----

Fixed bugs:
    - Fix edit triggers in open files popup (SplittableTabWidget)
    - Fix an issue which lead to corrupted recent files list (OpenCobolIDE/OpenCobolIDE#115)

2.6.1
-----

This is mostly a bug fix release with a few improvements here and there (fully backward compatible).

New features/Improvements:
    - Improve highlight occurences mode: the word under cursor is not highlighted anymore, only
      the other occurences are highlighted now. Also the original foreground color
      is now preserved.
    - Add missing PYGMENTS_STYLES list to public API (pyqode.core.api)
    - Improvre syntax highlighter: add format for namespace keywords and word operators
    - Improve ignore API of FSTreeView: add support for unix style wildcards (*.py,...)
    - Improve open files popup (splittable tab widget): use a table view instead of a list view

Fixed bugs:
    - Fix qt warning: QWidget::insertAction: Attempt to insert null action
    - Fix graphical bugs when a stylesheet has been setup on the application.
    - Fix issues whith show whitespaces
    - Fix unhandled exception in SubsequenceCompleter
    - Fix unhandled exception in FileManager.save
    - Fix runtime error with open files popup (splittable tab widget)

2.6.0
-----
New features:
    - Add a new filter mode for the code completion frontend: subsequence based
      matching (see pyQode/pyQode#1)
    - Improve cut/copy behaviour if there is no selected text (see pyQode/pyQode#29)
    - Add a new property for dynamic panel (see pyQode/pyQode#30)
    - Improve generic code folder for C based languages: add a
      CharBasedFoldDetector which works for C, C++, C#, PHP and Javascript
    - SplittableTabWidget: improve browsing when there are a lots of tab. There
      is now a hotkey (Ctrl+T by default) that shows a popup with a list of all
      the open files.
    - FileSystemTree: add a select method which allow for sync between a
      TabWidget and the FileSystemTree.
    - Implement EOL management: You can now define a preferred EOL to use when
      saving files and add the ability to detect exisiting EOL and use it
      instead of the preferred EOL.
    - Improve CI (travis): now tests are running for both PyQt4 and PyQt5
      on python 2.7, 3.2, 3.3 and 3.4
    - Add optional support for QtAwesome (icons)
    - SplittableTabWidget: add ability to setup custom context menu action on
      the tab bar.
    - SplittableTabWidget: improve names of tabs in case of duplicate filename.
    - Add support for stdeb: ppa packages will be available soon
    - Rework context menu: by default standard actions won't be created (copy,
      paste, ...). Those actions are handled by qt and make the context menu
      a bit messy.
    - Wheel support

Fixed bugs:
    - Fix an issue with draggable tabs on OSX (see pyQode/pyQode#31) and
      improve tab bar appearance on OSX (see pyQode/pyQode#37)
    - Fix a segfault with SplittableTabWidget (see pyQode/pyQode#32)
    - Fix get_linus_file_explorer on Ubuntu
    - Fix a few bugs with copy/paste operatins in FileSystemTree

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
