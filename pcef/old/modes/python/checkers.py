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
import sys
from pcef.modes.checker import CheckerMode, \
    ERROR_TYPE_WARNING, ERROR_TYPE_SYNTAX


class PEP8CheckerMode(CheckerMode):

    def onResultsAvailable(self, raw_results):
        """
        Decode and apply PEP8 results to the editor

        :param raw_results: the pep8 output string
        """
        lines = raw_results.splitlines()
        for line in lines:
            try:
                offset = 0
                if sys.platform == "win32":
                    offset = 1
                tokens = line.split(':')
                line_nr = int(tokens[1 + offset])
                col_nr = int(tokens[2 + offset])
                message = "PEP8: %s" % tokens[3 + offset]
                self.addError(
                    ERROR_TYPE_WARNING, line_nr, col_nr, message, True)
            except:
                pass

    def __init__(self):
        super(PEP8CheckerMode, self).__init__(
            "PEP8 Checker", "Check python code style using pep8.py",
            base_cmd="pep8")


class PyFlakesCheckerMode(CheckerMode):

    def onResultsAvailable(self, raw_results):
        """
        Decode and apply PyFlakes results to the editor

        :param raw_results: the pep8 output string
        """
        lines = raw_results.splitlines()
        for line in lines:
            try:
                tokens = line.split(':')
                nb_tokens = len(tokens)
                line_nr = int(tokens[nb_tokens - 2])
                message = "PyFlakes: %s" % tokens[nb_tokens - 1]
                error_type = ERROR_TYPE_SYNTAX
                # todo properly separate error messages from warning messages
                if "used" in message:
                    error_type = ERROR_TYPE_WARNING
                self.addError(error_type, line_nr, column=1, message=message,
                              selectLine=True)
            except ValueError:
                pass

    def __init__(self):
        super(PyFlakesCheckerMode, self).__init__(
            "PyFlakes Checker", "Checks python syntax errors using pyflakes.py",
            base_cmd="pyflakes")


class PyLintCheckerMode(CheckerMode):

    def onResultsAvailable(self, raw_results):
        """
        Decode and apply PyFlakes results to the editor

        :param raw_results: the pep8 output string
        """
        lines = raw_results.splitlines()
        for line in lines:
            try:
                tokens = line.split(':')
                nb_tokens = len(tokens)
                line_nr = int(tokens[nb_tokens - 2])
                message = "PyLint: %s" % tokens[nb_tokens - 1]
                error_type = ERROR_TYPE_SYNTAX
                if "[W" in message:
                    error_type = ERROR_TYPE_WARNING
                self.addError(error_type, line_nr, column=1, message=message,
                              selectLine=True)
            except ValueError:
                pass

    def __init__(self):
        super(PyLintCheckerMode, self).__init__(
            "Pylint Checker", "Checks python syntax errors using pylint.py",
            base_cmd="pylint -f parseable -rn -dC,R")