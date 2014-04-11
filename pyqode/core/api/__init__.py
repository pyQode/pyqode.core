"""
This package contains the public API for interacting with editor, client
side.

The API is a mostly procedural API that works on editor instance.

Originally most of those functions were methods of QCodeEdit, we moved them
in separates modules for the sake of readability.

The API can be divided into several parts:

    1) Extension API:

        Base classes for extending editor: Mode and panel and functions to
        add/remove/query modes and panels on editor.

        This is implemented in :mod:`api.extensions`

    2) QTextCursor/QTextDocument API

        A series of function to interact with the text document

        This is implemented in :mod:`api.text`

    3) Client/Server API

        A series of function to interacts with the pyqode server (start, stop,
        requests)

        This is implemented in :mod:`api.client`

    4) Text decorations API

        Classes and function to easily add decoration to the editor.

        This is implemented in :mod:`api.decorations`


    5) Syntax highlighter API

        The syntax highlighter base class and all the related classes (folding,
        symbol matcher,...)

        This is implemented in :mod:`api.syntax_highlighter`


While those parts have been implemented in different modules, them are all
available from the top level api package (i.e. you just need to import the
api package, no need to import submodules individually).

"""
# Extensions API
# Mode
from pyqode.core.api.extension import Mode
from pyqode.core.api.extension import get_mode
from pyqode.core.api.extension import get_modes
from pyqode.core.api.extension import install_mode
from pyqode.core.api.extension import uninstall_mode
# Panel
from pyqode.core.api.extension import Panel
from pyqode.core.api.extension import get_panel
from pyqode.core.api.extension import get_panels
from pyqode.core.api.extension import install_panel
from pyqode.core.api.extension import uninstall_panel

# Text API
from pyqode.core.api.text import clean_document
from pyqode.core.api.text import current_line_text
from pyqode.core.api.text import cursor_column_nbr
from pyqode.core.api.text import cursor_line_nbr
from pyqode.core.api.text import cursor_position
from pyqode.core.api.text import goto_line
from pyqode.core.api.text import line_count
from pyqode.core.api.text import line_nbr_from_position
from pyqode.core.api.text import line_pos_from_number
from pyqode.core.api.text import line_text
from pyqode.core.api.text import remove_last_line
from pyqode.core.api.text import select_lines
from pyqode.core.api.text import selected_text
from pyqode.core.api.text import selection_range
from pyqode.core.api.text import set_line_text
from pyqode.core.api.text import word_under_cursor
from pyqode.core.api.text import word_under_mouse_cursor

# Client API
from pyqode.core.api.client import connected_to_server
from pyqode.core.api.client import NotConnectedError
from pyqode.core.api.client import request_work
from pyqode.core.api.client import start_server
from pyqode.core.api.client import stop_server

# Decorations API
from pyqode.core.api.decoration import TextDecoration
from pyqode.core.api.decoration import TextDecorationSignals


# Utils API
from pyqode.core.api import utils