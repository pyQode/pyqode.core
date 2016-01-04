"""
This module contains a widget that can show the html preview of an
editor.
"""
from weakref import proxy
from pyqode.qt import QtCore, QtWebWidgets
from pyqode.core.api import DelayJobRunner


class HtmlPreviewWidget(QtWebWidgets.QWebView):
    def __init__(self, parent=None):
        super(HtmlPreviewWidget, self).__init__(parent)
        self._editor = None
        self._timer = DelayJobRunner(delay=1000)
        try:
            # prevent opening internal links when using QtWebKit
            self.page().setLinkDelegationPolicy(
                QtWebWidgets.QWebPage.DelegateAllLinks)
        except (TypeError, AttributeError):
            # no needed with QtWebEngine, internal links are properly handled
            # by the default implementation
            pass

    def set_editor(self, editor):
        try:
            self.setHtml(editor.to_html())
        except (TypeError, AttributeError):
            self.setHtml('<center>No preview available...</center>')
            self._editor = None
        else:
            if self._editor is not None and editor != self._editor:
                try:
                    self._editor.textChanged.disconnect(self._on_text_changed)
                except TypeError:
                    pass
            editor.textChanged.connect(self._on_text_changed)
            self._editor = proxy(editor)

    def _on_text_changed(self, *_):
        self._timer.request_job(self._update_preview)

    def _update_preview(self):
        try:
            pos = self.page().mainFrame().scrollBarValue(QtCore.Qt.Vertical)
            self.setHtml(self._editor.to_html())
            self.page().mainFrame().setScrollBarValue(QtCore.Qt.Vertical, pos)
        except AttributeError:
            # Not possible with QtWebEngine???
            # self._scroll_pos = self.page().mainFrame().scrollBarValue(
                # QtCore.Qt.Vertical)
            self.setHtml(self._editor.to_html())
