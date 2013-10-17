import sys
from pyqode.qt import QtGui
import pyqode.core


def main():
    app = QtGui.QApplication(sys.argv)
    code_edit = pyqode.core.QCodeEdit()
    print("QCodeEdit:")
    print("-------------------")
    print(code_edit.settings.dump())
    print(code_edit.style.dump())

    print()

    print("QGenericCodeEdit:")
    print("-------------------")
    generic_code_edit = pyqode.core.QGenericCodeEdit()
    print(generic_code_edit.settings.dump())
    print(generic_code_edit.style.dump())


if __name__ == "__main__":
    main()
