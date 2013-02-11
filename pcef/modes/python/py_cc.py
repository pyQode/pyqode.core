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
         'Module': '',
         'Function': ':/icons/rc/method.png'}


class PythonCompletionModel(CompletionModel):
    def update(self, source_code, line, col, filename, encoding):
        script = Script(source_code, line, col, filename, encoding)
        completions = script.complete()
        call = script.get_in_function_call()
        print "----------------------------"
        if call is not None:
            for p in call.params:
                print p
        self._suggestions[:] = []
        for completion in completions:
            desc = completion.description
            ctype = desc.split(':')[0]
            icon = None
            if ctype in Icons:
                icon = QIcon(Icons[ctype])
            self._suggestions.append(Suggestion(completion.word, icon=icon, description=desc.split(':')[1]))
