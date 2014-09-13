"""
This module contains the occurrences highlighter mode.
"""
from pyqode.qt import QtGui
from pyqode.core.api import Mode, DelayJobRunner, TextHelper, TextDecoration
from pyqode.core.backend import NotConnected
from pyqode.core.backend.workers import findall


class OccurrencesHighlighterMode(Mode):
    """
    This mode highlights occurrences of word under the text text cursor.

    The ``delay`` before searching for occurrences is configurable.
    """
    @property
    def delay(self):
        return self.timer.delay

    @delay.setter
    def delay(self, value):
        self.timer.delay = value

    def __init__(self):
        super(OccurrencesHighlighterMode, self).__init__()
        self._decorations = []
        self.timer = DelayJobRunner()
        self._sub = None

    def on_state_changed(self, state):
        if state:
            self.editor.cursorPositionChanged.connect(self._request_highlight)
        elif state:
            self.editor.cursorPositionChanged.disconnect(
                self._request_highlight)
            self.timer.cancel_requests()

    def _clear_decos(self):
        for d in self._decorations:
            self.editor.decorations.remove(d)
        self._decorations[:] = []

    def _request_highlight(self):
        sub = TextHelper(self.editor).word_under_cursor(
            select_whole_word=True).selectedText()
        if self.editor is not None and sub != self._sub:
            self._clear_decos()
            self.timer.request_job(self._send_request)

    def _send_request(self):
        if (self.editor is not None and
                not self.editor.textCursor().hasSelection()):
            self._sub = TextHelper(self.editor).word_under_cursor(
                select_whole_word=True).selectedText()
            request_data = {
                'string': self.editor.toPlainText(),
                'sub': self._sub,
                'regex': False,
                'whole_word': True,
                'case_sensitive': True
            }
            try:
                self.editor.backend.send_request(findall, request_data,
                                                 self._on_results_available)
            except NotConnected:
                self._request_highlight()

    def _on_results_available(self, _, results):
        if len(results) > 1:
            for start, end in results:
                deco = TextDecoration(self.editor.textCursor(),
                                      start_pos=start, end_pos=end)
                deco.set_background(QtGui.QBrush(QtGui.QColor('#80CC80')))
                deco.set_foreground(QtGui.QColor('#404040'))
                deco.draw_order = 3
                self.editor.decorations.append(deco)
                self._decorations.append(deco)
