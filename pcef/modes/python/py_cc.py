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
"""
This modules contains the python specific code completion model.

Python code completion is achieved by the use of the awesome **jedi** library (https://github.com/davidhalter/jedi)
"""
from PySide.QtGui import QIcon
from jedi import Script
from pcef.modes.cc import CompletionModel
from pcef.modes.cc import Suggestion

Icons = {'Class': ':/icons/rc/class.png',
         'Import': ':/icons/rc/import.png',
         'Statement': ':/icons/rc/var.png',
         'Module': ':/icons/rc/module.png',
         'Param': ':/icons/rc/param.png',
         'Function': ':/icons/rc/method.png'}


class PythonCompletionModel(CompletionModel):
    def update(self, source_code, line, col, filename, encoding):
        # complete with jedi

        try:
            script = Script(source_code, line, col, filename, encoding)
            completions = script.complete()
            # clean suggestion list
            self._suggestions[:] = []
            for completion in completions:
                # get type from description
                desc = completion.description
                suggestionType = desc.split(':')[0]
                # get the associated icon if any
                icon = None
                if suggestionType in Icons:
                    icon = Icons[suggestionType]
                # add the suggestion to the list
                self._suggestions.append(Suggestion(completion.word, icon=icon, description=desc.split(':')[1]))
        except :
            pass
