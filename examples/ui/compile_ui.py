#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This scripts compile the ui and qrc files using pyqt4 dev tools then modify
them to use PyQt4 instead of pyqt4. It also adapts the rc imports so that
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
        new_lines.append(l)
    with open(script, 'w') as f_script:
        f_script.write("\n".join(new_lines))


def main():
    # ui scripts
    for ui_file in glob.glob("*.ui"):
        base_name = os.path.splitext(ui_file)[0]
        dst = "%s_ui.py" % base_name
        cmd = "pyuic4 %s -o %s" % (ui_file, dst)
        print(cmd)
        os.system(cmd)
        fix_script(dst)

    # rc scripts
    for rc_file in glob.glob("*.qrc"):
        base_name = os.path.splitext(rc_file)[0]
        dst = "%s_rc.py" % base_name
        cmd = "pyrcc4 -py3 %s -o %s" % (rc_file, dst)
        print(cmd)
        os.system(cmd)
        fix_script(dst)

if __name__ == "__main__":
    main()
