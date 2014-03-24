#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#The MIT License (MIT)
#
#Copyright (c) <2013-2014> <Colin Duquesnoy and others, see AUTHORS.txt>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#
"""
This module contains the code completion mode and the related classes.
"""
import re
from pyqode.core.api import constants
from pyqode.core.api import workers
from pyqode.core.editor import Mode
from pyqode.core.api.system import DelayJobRunner, memoized
from PyQt4 import QtGui, QtCore
from pyqode.core import logger


class CodeCompletionMode(Mode, QtCore.QObject):
    """
    This mode provides code completion system wich is extensible. It takes care
    of running the completion request in a background process using one or more
    completion provider(s).

    To implement a code completion for a specific language, you only need to
    implement new :class:`pyqode.core.CompletionProvider`

    The completion popup is shown the user press **ctrl+space** or
    automatically while the user is typing some code (this can be configured
    using a series of properties described in the below table).

    .. note:: The code completion mode automatically starts a unique subprocess
              (:attr:`pyqode.core.CodeCompletionMode.SERVER`)
              to run code completion tasks. This process is automatically
              closed when the application is about to quit. You can use this
              process to run custom task on the completion process (e.g.
              setting up some :py:attr:`sys.modules`).
    """
    #: Mode identifier
    IDENTIFIER = "codeCompletionMode"
    #: Mode description
    DESCRIPTION = "Provides a code completion/suggestion system"

    @property
    def trigger_key(self):
        return self.editor.style.value("triggerKey", section="Code completion")

    @trigger_key.setter
    def trigger_key(self, value):
        self.editor.style.set_value(
            "triggerKey", value, section="Code Completion")

    @property
    def trigger_length(self):
        return self.editor.style.value(
            "triggerLength", section="Code completion")

    @trigger_length.setter
    def trigger_length(self, value):
        self.editor.style.set_value(
            "triggerLength", value, section="Code completion")

    @property
    def trigger_symbols(self):
        return self.editor.style.value(
            "triggerSymbols", section="Code completion")

    @trigger_symbols.setter
    def trigger_symbols(self, value):
        self.editor.style.set_value(
            "triggerSymbols", value, section="Code completion")

    @property
    def show_tooltips(self):
        return self.editor.style.value(
            "showTooltips", section="Code completion")

    @show_tooltips.setter
    def show_tooltips(self, value):
        self.editor.style.set_value(
            "showTooltips", value, section="Code completion")

    @property
    def case_sensitive(self):
        return self.editor.style.value(
            "caseSensitive", section="Code completion")

    @case_sensitive.setter
    def case_sensitive(self, value):
        self.editor.style.set_value(
            "caseSensitive", value, section="Code completion")

    @property
    def completion_prefix(self):
        """
        Returns the current completion prefix
        """
        prefix = self.editor.select_word_under_cursor().selectedText()
        if prefix == "":
            try:
                prefix = self.editor.select_word_under_cursor(
                    select_whole_word=True).selectedText()[0]
            except IndexError:
                pass
        return prefix.strip()

    def __init__(self, server_port=5000):
        """
        :param server_port: Local TCP/IP port to use to start the code
                            completion server process
        """
        Mode.__init__(self)
        QtCore.QObject.__init__(self)
        self._current_completion = ""
        self._trigger_key = None
        # use to display a waiting cursor if completion provider takes too much
        # time
        self._job_runner = DelayJobRunner(self, nb_threads_max=1, delay=1000)
        self._tooltips = {}
        self._cursor_line = -1
        self._cancel_next = False
        self._request_cnt = 0
        self._last_completion_prefix = ""
        self._server_port = server_port

    def request_completion(self):
        """
        Requests a code completion at the current cursor position.
        """
        if self._request_cnt:
            return
        # only check first byte
        column = self.editor.cursor_position[1]
        usd = self.editor.textCursor().block().userData()
        for start, end in usd.cc_disabled_zones:
            if start <= column < end:
                logger.debug("Cancel request, cursor is in a disabled zone")
                return
        self._request_cnt += 1
        self._collect_completions(
            self.editor.toPlainText(), self.editor.cursor_position[0],
            self.editor.cursor_position[1], self.editor.file_path,
            self.editor.file_encoding, self.completion_prefix)

    def _on_install(self, editor):
        self._completer = QtGui.QCompleter([""], editor)
        self._completer.setCompletionMode(self._completer.PopupCompletion)
        self._completer.activated.connect(self._insert_completion)
        self._completer.highlighted.connect(
            self._on_selected_completion_changed)
        self._completer.setModel(QtGui.QStandardItemModel())
        Mode._on_install(self, editor)
        self.editor.settings.add_property(
            "triggerKey", int(QtCore.Qt.Key_Space), section="Code completion")
        self._trigger_len = self.editor.settings.add_property(
            "triggerLength", 1, section="Code completion")
        self.editor.settings.add_property(
            "triggerSymbols", ["."], section="Code completion")
        # todo to removed, replaced by trigger symbols
        self.editor.settings.add_property(
            "triggerKeys", [int(QtCore.Qt.Key_Period)],
            section="Code completion")
        self.editor.settings.add_property("showTooltips", True,
                                          section="Code completion")
        self.editor.settings.add_property("caseSensitive", False,
                                          section="Code completion")

    def _on_uninstall(self):
        self._completer = None

    def _on_state_changed(self, state):
        if state:
            self.editor.focused_in.connect(self._on_focus_in)
            self.editor.key_pressed.connect(self._on_key_pressed)
            self.editor.post_key_pressed.connect(self._on_key_released)
            self._completer.highlighted.connect(
                self._display_completion_tooltip)
            self.editor.cursorPositionChanged.connect(
                self._on_cursor_position_changed)
        else:
            self.editor.focused_in.disconnect(self._on_focus_in)
            self.editor.key_pressed.disconnect(self._on_key_pressed)
            self.editor.post_key_pressed.disconnect(self._on_key_released)
            self._completer.highlighted.disconnect(
                self._display_completion_tooltip)
            self.editor.cursorPositionChanged.disconnect(
                self._on_cursor_position_changed)
            self.editor.new_text_set.disconnect(self.requestPreload)

    def _on_focus_in(self, event):
        """
        Resets completer widget

        :param event: QFocusEvents
        """
        self._completer.setWidget(self.editor)

    def _on_results_available(self, status, results):
        logger.debug("got completion results")
        self.editor.set_cursor(QtCore.Qt.IBeamCursor)
        all_results = []
        if status:
            for res in results:
                all_results += res
        self._request_cnt -= 1
        self._show_completions(all_results)

    def _on_key_pressed(self, event):
        QtGui.QToolTip.hideText()
        is_shortcut = self._is_shortcut(event)
        # handle completer popup events ourselves
        if self._completer.popup().isVisible():
            self._handle_completer_events(event)
            if is_shortcut:
                event.accept()
        if is_shortcut:
            self.request_completion()
            event.accept()

    @staticmethod
    def _is_navigation_key(event):
        return (event.key() == QtCore.Qt.Key_Backspace or
                event.key() == QtCore.Qt.Key_Back or
                event.key() == QtCore.Qt.Key_Delete or
                event.key() == QtCore.Qt.Key_Left or
                event.key() == QtCore.Qt.Key_Right or
                event.key() == QtCore.Qt.Key_Up or
                event.key() == QtCore.Qt.Key_Down or
                event.key() == QtCore.Qt.Key_Space or
                event.key() == QtCore.Qt.Key_End or
                event.key() == QtCore.Qt.Key_Home)

    @staticmethod
    def _is_end_of_word_char(event, is_printable, symbols):
        ret_val = False
        if is_printable and symbols:
            k = event.text()
            seps = constants.WORD_SEPARATORS
            ret_val = (k in seps and not k in symbols)
        return ret_val

    def _on_key_released(self, event):
        if self._is_shortcut(event):
            return
        is_printable = self._is_printable_key_event(event)
        is_navigation_key = self._is_navigation_key(event)
        symbols = self.editor.settings.value(
            "triggerSymbols", section="Code completion")
        is_end_of_word = self._is_end_of_word_char(
            event, is_printable, symbols)
        if self._completer.popup().isVisible():
            # Update completion prefix
            self._completer.setCompletionPrefix(self.completion_prefix)
            cnt = self._completer.completionCount()
            if (not cnt or (self.completion_prefix == "" and is_navigation_key)
                or is_end_of_word or
                    (int(event.modifiers()) and event.key() ==
                        QtCore.Qt.Key_Backspace)):
                self._hide_popup()
            else:
                self._show_popup()
        # text triggers
        if is_printable:
            if event.text() == " ":
                self._cancel_next = self._request_cnt
            else:
                # trigger symbols
                if symbols:
                    tc = self.editor.select_word_under_cursor()
                    tc.setPosition(tc.position())
                    tc.movePosition(tc.StartOfLine, tc.KeepAnchor)
                    text_to_cursor = tc.selectedText()
                    for symbol in symbols:
                        if text_to_cursor.endswith(symbol):
                            logger.debug("CC: Symbols trigger")
                            self._hide_popup()
                            self.request_completion()
                            return
                # trigger length
                if not self._completer.popup().isVisible():
                    prefix_len = len(self.completion_prefix)
                    if prefix_len == self.editor.settings.value(
                            "triggerLength", section="Code completion"):
                        logger.debug("CC: Len trigger")
                        self.request_completion()
                        return
            if self.completion_prefix == "":
                return self._hide_popup()

    def _on_selected_completion_changed(self, completion):
        self._current_completion = completion

    def _on_cursor_position_changed(self):
        cl = self.editor.cursor_position[0]
        if cl != self._cursor_line:
            self._cursor_line = cl
            self._hide_popup()
            self._job_runner.cancel_requests()
            self._job_runner.stop_job()

    @QtCore.pyqtSlot()
    def _set_wait_cursor(self):
        self.editor.set_cursor(QtCore.Qt.WaitCursor)

    def _is_last_char_end_of_word(self):
        try:
            tc = self.editor.select_word_under_cursor()
            tc.setPosition(tc.position())
            tc.movePosition(tc.StartOfLine, tc.KeepAnchor)
            l = tc.selectedText()
            last_char = l[len(l) - 1]
            if last_char != ' ':
                symbols = self.editor.settings.value(
                    "triggerSymbols", section="Code completion")
                seps = constants.WORD_SEPARATORS
                return last_char in seps and not last_char in symbols
            return False
        except IndexError:
            return False
        except TypeError:
            return False  # no symbols

    def _show_completions(self, completions):
        self._job_runner.cancel_requests()
        # user typed too fast: end of word char has been inserted
        if self._is_last_char_end_of_word():
            return
        # user typed too fast: the user already typed the only suggestion we
        # have
        elif (len(completions) == 1 and
              completions[0]['name'] == self.completion_prefix):
            return
        # a request cancel has been set
        if self._cancel_next:
            self._cancel_next = False
            return
        # we can show the completer
        self._update_model(completions, self._completer.model())
        self._show_popup()
        # self.editor.viewport().setCursor(QtCore.Qt.IBeamCursor)

    def _handle_completer_events(self, event):
        # complete
        if (event.key() == QtCore.Qt.Key_Enter or
                event.key() == QtCore.Qt.Key_Return):
            self._insert_completion(self._current_completion)
            self._hide_popup()
            event.accept()
            return True
        # hide
        elif (event.key() == QtCore.Qt.Key_Escape or
                event.key() == QtCore.Qt.Key_Backtab):
            self._hide_popup()
            event.accept()
            return True
        return False

    def _hide_popup(self):
        # self.editor.viewport().setCursor(QtCore.Qt.IBeamCursor)
        self._completer.popup().hide()
        self._job_runner.cancel_requests()
        QtGui.QToolTip.hideText()

    def _show_popup(self):
        cnt = self._completer.completionCount()
        full_prefix = self.editor.select_word_under_cursor(
            select_whole_word=True).selectedText()
        if (full_prefix == self._current_completion) and cnt == 1:
            self._hide_popup()
        else:
            if self.editor.settings.value("caseSensitive",
                                          section="Code completion"):
                self._completer.setCaseSensitivity(QtCore.Qt.CaseSensitive)
            else:
                self._completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
            # set prefix
            self._completer.setCompletionPrefix(self.completion_prefix)
            # compute size and pos
            cr = self.editor.cursorRect()
            char_width = self.editor.fontMetrics().width('A')
            prefix_len = (len(self.completion_prefix) * char_width)
            cr.translate(self.editor.margin_size() - prefix_len,
                         self.editor.margin_size(0))
            w = self._completer.popup().verticalScrollBar().sizeHint().width()
            cr.setWidth(self._completer.popup().sizeHintForColumn(0) + w)
            # show the completion list
            self._completer.complete(cr)
            self._completer.popup().setCurrentIndex(
                self._completer.completionModel().index(0, 0))

    def _insert_completion(self, completion):
        tc = self.editor.select_word_under_cursor(select_whole_word=True)
        tc.insertText(completion)
        self.editor.setTextCursor(tc)

    def _is_shortcut(self, event):
        """
        Checks if the event's key and modifiers make the completion shortcut
        (Ctrl+M)

        :param event: QKeyEvent

        :return: bool
        """
        val = int(event.modifiers() & QtCore.Qt.ControlModifier)
        trigger_key = int(self.editor.settings.value(
            "triggerKey", section="Code completion"))
        return val and event.key() == trigger_key

    @staticmethod
    def strip_control_characters(input):
        if input:
            # unicode invalid characters
            re_illegal = \
                '([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + \
                '|' + \
                '([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \
                (chr(0xd800), chr(0xdbff), chr(0xdc00), chr(0xdfff),
                 chr(0xd800), chr(0xdbff), chr(0xdc00), chr(0xdfff),
                 chr(0xd800), chr(0xdbff), chr(0xdc00), chr(0xdfff))
            input = re.sub(re_illegal, "", input)
            # ascii control characters
            input = re.sub(r"[\x01-\x1F\x7F]", "", input)
        return input

    @staticmethod
    def _is_printable_key_event(event):
        return len(CodeCompletionMode.strip_control_characters(
            event.text())) == 1

    @staticmethod
    @memoized
    def _make_icon(icon):
        return QtGui.QIcon(icon)

    def _update_model(self, completions, cc_model):
        """
        Creates a QStandardModel that holds the suggestion from the completion
        models for the QCompleter

        :param completionPrefix:
        """
        # build the completion model
        cc_model.clear()
        displayed_texts = []
        self._tooltips.clear()
        for completion in completions:
            name = completion['name']
            if not name:
                continue
            # skip redundant completion
            if name != self.completion_prefix and \
                    not name in displayed_texts:
                displayed_texts.append(name)
                item = QtGui.QStandardItem()
                item.setData(name, QtCore.Qt.DisplayRole)
                if 'tooltip' in completion and completion['tooltip']:
                    self._tooltips[name] = completion['tooltip']
                if 'icon' in completion:
                    item.setData(self._make_icon(completion['icon']),
                                 QtCore.Qt.DecorationRole)
                cc_model.appendRow(item)
        return cc_model

    def _display_completion_tooltip(self, completion):
        if not self.editor.settings.value("showTooltips",
                                          section="Code completion"):
            return
        if not completion in self._tooltips:
            QtGui.QToolTip.hideText()
            return
        if completion in self._tooltips:
            tooltip = self._tooltips[completion].strip()
        else:
            tooltip = None
        if tooltip:
            pos = self._completer.popup().pos()
            pos.setX(pos.x() + self._completer.popup().size().width())
            pos.setY(pos.y() - 15)
            QtGui.QToolTip.showText(pos, tooltip, self.editor)
        else:
            QtGui.QToolTip.hideText()

    def _collect_completions(self, code, line, column, path, encoding,
                             completion_prefix):
        logger.debug("Completion requested")
        data = {'code': code, 'line': line, 'column': column,
                'path': path, 'encoding': encoding,
                'prefix': completion_prefix}
        self.editor.request_work(workers.CodeCompletion, args=data,
                                 on_receive=self._on_results_available)
        self._set_wait_cursor()
