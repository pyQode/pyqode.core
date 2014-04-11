"""
This package contains the API for interacting with the frontend (client side
GUI).

The API is a mostly procedural API that works on QCodeEdit instance.

Originally most of those functions were methods of QCodeEdit, we moved them
in separates modules for the sake of readability.

The API can be divided into several parts:

    1) QCodeEdit API:

        The code editor widget class.

    2) Extension API:

        Base classes for extending editor: Mode and panel and functions to
        add/remove/query modes and panels on editor.

        This is implemented in :mod:`frontend.extensions`. Builtin modes and
        panels are stored in a specific package: frontend.modes and
        frontend.panels.

    3) QTextCursor/QTextDocument API

        A series of function to interact with the text document

        This is implemented in :mod:`frontend.text`

    4) Client/Server API

        A series of function to interacts with the pyqode server (start, stop,
        requests)

        This is implemented in :mod:`frontend.client`

    5) Text decorations API

        Classes and function to easily add decoration to the editor.

        This is implemented in :mod:`frontend.decorations`


    6) Syntax highlighter API

        The syntax highlighter base class and all the related classes (folding,
        symbol matcher,...)

        This is implemented in :mod:`frontend.syntax_highlighter`


While those parts have been implemented in different modules, them are all
available from the top level frontend package (i.e. you just need to import the
frontend package, no need to import submodules individually).

"""
# QCodeEdit
from pyqode.core.frontend.code_edit import QCodeEdit

# Extensions API
# Mode
from pyqode.core.frontend.extension import Mode
from pyqode.core.frontend.extension import get_mode
from pyqode.core.frontend.extension import get_modes
from pyqode.core.frontend.extension import install_mode
from pyqode.core.frontend.extension import uninstall_mode
# Panel
from pyqode.core.frontend.extension import Panel
from pyqode.core.frontend.extension import get_panel
from pyqode.core.frontend.extension import get_panels
from pyqode.core.frontend.extension import install_panel
from pyqode.core.frontend.extension import uninstall_panel

# Text API
from pyqode.core.frontend.text import clean_document
from pyqode.core.frontend.text import current_line_text
from pyqode.core.frontend.text import cursor_column_nbr
from pyqode.core.frontend.text import cursor_line_nbr
from pyqode.core.frontend.text import cursor_position
from pyqode.core.frontend.text import goto_line
from pyqode.core.frontend.text import line_count
from pyqode.core.frontend.text import line_nbr_from_position
from pyqode.core.frontend.text import line_pos_from_number
from pyqode.core.frontend.text import line_text
from pyqode.core.frontend.text import remove_last_line
from pyqode.core.frontend.text import select_lines
from pyqode.core.frontend.text import selected_text
from pyqode.core.frontend.text import selection_range
from pyqode.core.frontend.text import set_line_text
from pyqode.core.frontend.text import word_under_cursor
from pyqode.core.frontend.text import word_under_mouse_cursor

# Client API
from pyqode.core.frontend.client import connected_to_server
from pyqode.core.frontend.client import NotConnectedError
from pyqode.core.frontend.client import request_work
from pyqode.core.frontend.client import start_server
from pyqode.core.frontend.client import stop_server

# Text decorations API
from pyqode.core.frontend.decoration import TextDecoration
from pyqode.core.frontend.decoration import _TextDecorationSignals
from pyqode.core.frontend.decoration import add_decoration
from pyqode.core.frontend.decoration import remove_decoration
from pyqode.core.frontend.decoration import clear_decorations


# Utils API
from pyqode.core.frontend import utils
