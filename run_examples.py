#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# <Project>
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import sys
from PySide.QtGui import QApplication
from examples import generic_example
EXAMPLES_NAMES = ["Generic editor"]
EXAMPLES_FUNCTIONS = [generic_example.main]


def main():
    # create a unique QApplication
    app = QApplication(sys.argv)
    # print menu
    print "Here is the list of examples:"
    for i, example in enumerate(EXAMPLES_NAMES):
        print "  {0}: {1}".format(i + 1, example)

    do_continue = True
    while do_continue:
        # get input
        choice = -1
        while choice < 0 or choice >= len(EXAMPLES_NAMES):
            buf = raw_input("Enter the example number: ")
            try:
                choice = int(buf) - 1
            except ValueError:
                choice = -1

        # run the example
        print "Running {0}".format(EXAMPLES_NAMES[choice])
        EXAMPLES_FUNCTIONS[choice](app)

        buf = raw_input("Do you want to try another example? (yes/no)\n")
        if not buf == "yes":
            do_continue = False


if __name__ == "__main__":
    main()
