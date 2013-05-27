import os
import sys
import pcef


def main():
    app = pcef.QtGui.QApplication(sys.argv)
    editor = pcef.genericEditor()
    editor.style.open(os.path.join(pcef.findSettingsDirectory(),
                                   "default_style.json"))
    editor.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
