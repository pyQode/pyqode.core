#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This scripts compile the forms and qrc files using pyqt5-dev-tools then modify
them to use pyqode.qt instead of PyQt5. It also adapts the rc imports so that
they works with python3
"""
import glob
import os


def fix_script(script):
    with open(script, 'r') as f_script:
        lines = f_script.read().splitlines()
    new_lines = []
    for l in lines:
        if l.startswith("import "):
            l = "from . " + l
        if "from PyQt5 import" in l:
            l = l.replace("from PyQt5 import", "from pyqode.qt import")
        new_lines.append(l)
    with open(script, 'w') as f_script:
        f_script.write("\n".join(new_lines))


def main():
    # forms scripts
    for ui_file in glob.glob("*.forms"):
        base_name = os.path.splitext(ui_file)[0]
        dst = "%s_ui.py" % base_name
        cmd = "pyuic5 --from-import %s -o %s" % (ui_file, dst)
        print(cmd)
        os.system(cmd)
        fix_script(dst)

    # rc scripts
    for rc_file in glob.glob("*.qrc"):
        base_name = os.path.splitext(rc_file)[0]
        dst = "%s_rc.py" % base_name
        cmd = "pyrcc5 %s -o %s" % (rc_file, dst)
        print(cmd)
        os.system(cmd)
        fix_script(dst)

if __name__ == "__main__":
    main()
