from pcef import saveFileFromEditor
from pcef.core import Mode


class AutoSaveMode(Mode):
    """
    Your mode documentation goes here
    """
    NAME = "Autosave"
    DESCRIPTION = "Automatically save whenever the text changed"

    def __init__(self):
        Mode.__init__(self, self.NAME, self.DESCRIPTION)

    def _onStateChanged(self, state):
        """
        Called when the mode is activated/deactivated
        """
        if state:
            self.editor.codeEdit.textChanged.connect(self.__save)
        else:
            self.editor.codeEdit.textChanged.disconnect(self.__save)

    def __save(self):
        saveFileFromEditor(self.editor)
