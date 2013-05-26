import sys
import pcef


def main():
    app = pcef.QtGui.QApplication(sys.argv)
    editor = pcef.genericEditor()
    editor.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
