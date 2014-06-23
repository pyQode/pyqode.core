from pyqode.core.api.mode import Mode
from pyqode.core.qt import QtGui, QtCore


class SyntaxHighlighter(QtGui.QSyntaxHighlighter, Mode):
    """
    Abstract Base class for syntax highlighter modes.

    It fills up the document with our custom user data, setup the parenthesis
    infos and run the FoldDetector on every text block. It **does not do any
    syntax highlighting**, this task is left to the sublasses such as
    :class:`pyqode.core.modes.PygmentsSyntaxHighlighter`.

    Subclasses **must** override the
    :meth:`pyqode.core.api.SyntaxHighlighter.highlight_block` method to
    apply custom highlighting.

    **signals**:
      - :attr:`pyqode.core.api.SyntaxHighlighter.block_highlight_started`
      - :attr:`pyqode.core.api.SyntaxHighlighter.block_highlight_finished`

    .. warning:: You should always inherit from this class to create a new
                 syntax highlighter mode.

                 **Never inherit directly from QSyntaxHighlighter.**
    """
    class ParenthesisInfo(object):
        """
        Stores information about a parenthesis in a line of code.
        """
        # pylint: disable=too-few-public-methods
        def __init__(self, pos, char):
            #: Position of the parenthesis, expressed as a number of character
            self.position = pos
            #: The parenthesis character, one of "(", ")", "{", "}", "[", "]"
            self.character = char

    #: Signal emitted at the start of highlightBlock. Parameters are the
    #: highlighter instance and the current text block
    block_highlight_started = QtCore.Signal(object, object)

    #: Signal emitted at the end of highlightBlock. Parameters are the
    #: highlighter instance and the current text block
    block_highlight_finished = QtCore.Signal(object, object)

    def __init__(self, parent):
        QtGui.QSyntaxHighlighter.__init__(self,  parent)
        Mode.__init__(self)
        self._spaces_ptrn = QtCore.QRegExp(r'\s+')
        # there is a bug with QTextBlockUserData in PyQt5, we need to
        # keep a reference on them, otherwise they are removed from memory.
        self._blocks = set()
        #: Set this flag to true to process events when a line is highlighted.
        self.process_events_on_highlight = False

    def __del__(self):
        self._blocks.clear()

    def set_mime_type(self, mime_type):
        """ Sets the associated mime type and update the internal lexer """
        pass

    @staticmethod
    def _detect_parentheses(text, user_data):
        """ Detect symbols (parentheses, braces, ...)
        """
        user_data.parentheses[:] = []
        user_data.square_brackets[:] = []
        user_data.braces[:] = []
        # todo check if bracket is not into a string litteral
        # parentheses
        left_pos = text.find("(", 0)
        while left_pos != -1:
            info = SyntaxHighlighter.ParenthesisInfo(left_pos, "(")
            user_data.parentheses.append(info)
            left_pos = text.find("(", left_pos + 1)
        right_pos = text.find(")", 0)
        while right_pos != -1:
            info = SyntaxHighlighter.ParenthesisInfo(right_pos, ")")
            user_data.parentheses.append(info)
            right_pos = text.find(")", right_pos + 1)
        # braces
        left_pos = text.find("{", 0)
        while left_pos != -1:
            info = SyntaxHighlighter.ParenthesisInfo(left_pos, "{")
            user_data.braces.append(info)
            left_pos = text.find("{", left_pos + 1)
        right_pos = text.find("}", 0)
        while right_pos != -1:
            info = SyntaxHighlighter.ParenthesisInfo(right_pos, "}")
            user_data.braces.append(info)
            right_pos = text.find("}", right_pos + 1)
        # square_brackets
        left_pos = text.find("[", 0)
        while left_pos != -1:
            info = SyntaxHighlighter.ParenthesisInfo(left_pos, "[")
            user_data.square_brackets.append(info)
            left_pos = text.find("[", left_pos + 1)
        right_pos = text.find("]", 0)
        while right_pos != -1:
            info = SyntaxHighlighter.ParenthesisInfo(right_pos, "]")
            user_data.square_brackets.append(info)
            right_pos = text.find("]", right_pos + 1)
        user_data.parentheses[:] = sorted(
            user_data.parentheses, key=lambda x: x.position)
        user_data.square_brackets[:] = sorted(
            user_data.square_brackets, key=lambda x: x.position)
        user_data.braces[:] = sorted(
            user_data.braces, key=lambda x: x.position)

    def highlightBlock(self, text):  #: pylint: disable=invalid-name
        """
        Highlights a block of text.
        """
        self.block_highlight_started.emit(self, text)
        # setup user data
        user_data = self.currentBlockUserData()
        if not user_data:
            user_data = TextBlockUserData()
        # update user data
        user_data.line_number = self.currentBlock().blockNumber() + 1
        self._blocks.add(user_data)
        self.setCurrentBlockUserData(user_data)
        self.setCurrentBlockState(0)
        self._detect_parentheses(text, user_data)
        self.highlight_block(text)
        self.block_highlight_finished.emit(self, text)

    def highlight_block(self, text):
        """
        Abstract method. Override this to apply syntax highlighting.

        :param text: Line of text to highlight.
        """
        raise NotImplementedError()


class TextBlockUserData(QtGui.QTextBlockUserData):
    """
    Custom text block data. pyQode use text block data for many purposes:
        - folding detection
        - symbols matching
        - mar

    You can also add your own data.
    """
    # pylint: disable=too-many-instance-attributes, too-few-public-methods
    def __init__(self):
        super().__init__()
        #: Line number of the data, for convenience
        self.line_number = -1
        #: Specify if the block is folded
        self.folded = False
        #: Specify if the block is a fold start
        self.fold_start = False
        #: The block's fold indent
        self.fold_indent = -1
        #: The :class:`pyqode.core.Marker` associated with the text block
        self.marker = None
        #: List of :class:`pyqode.core.ParenthesisInfo` for the "(" and ")"
        #: symbols
        self.parentheses = []
        #: List of :class:`pyqode.core.ParenthesisInfo` for the "[" and "]"
        #: symbols
        self.square_brackets = []
        #: List of :class:`pyqode.core.ParenthesisInfo` for the "{" and "}"
        #: symbols
        self.braces = []
        #: Zones were Code completion is disabled. List of tuple. Each tuple
        #: contains the start column and the end column.
        self.cc_disabled_zones = []

    def __repr__(self):
        return ("#{} - Folded: {}  FoldIndent: {} - FoldStart: {}".format(
            self.line_number, self.folded, self.fold_indent, self.fold_start))