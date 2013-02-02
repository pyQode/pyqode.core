#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - PySide Code Editing framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
from pcef.base import Mode


class CompletionModel(object):
    def update(self):
        pass


class CodeCompletionMode(Mode):
    """
    Code completion mode provides code completion to the text edit.

    The list of suggestion is supplied by a CodeCompletionModel. The mode can
    use several completion model with an order of priority. For example, in a
    python editor, we might have a smart completion model that would be use
    primarily and another basic document word completion as a fallback system
    when the smart system fails to provide enough suggestions.

    The mode use a QCompleter to provides the list of suggestions.
    """