#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - Python/Qt Code Editing Framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
This package contains the core modes (language independant)
"""
from pcef.core.modes.caret_line_highlight import CaretLineHighlighterMode
from pcef.core.modes.right_margin import RightMarginMode
from pcef.core.modes.zoom import ZoomMode
from pcef.core.modes.pygments_syntax_highlighter import \
    PygmentSyntaxHighlighterMode