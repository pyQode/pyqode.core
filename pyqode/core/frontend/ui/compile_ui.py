# -*- coding: utf-8 -*-
"""
This scripts compile the ui and qrc files using pyside dev tools then modify
them to use PyQt5 instead of PySide. It also adapts the rc imports so that
they works with python3
"""
import glob
import os


def main():
    # ui scripts
    for ui_file in glob.glob("*.ui"):
        base_name = os.path.splitext(ui_file)[0]
        dst = "%s_ui.py" % base_name
        cmd = "pyuic5 --from-import %s -o %s" % (ui_file, dst)
        print(cmd)
        os.system(cmd)

    # rc scripts
    for rc_file in glob.glob("*.qrc"):
        base_name = os.path.splitext(rc_file)[0]
        dst = "%s_rc.py" % base_name
        cmd = "pyrcc5 %s -o %s" % (rc_file, dst)
        print(cmd)
        os.system(cmd)

if __name__ == "__main__":
    main()
