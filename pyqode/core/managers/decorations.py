"""
Contains the text decorations manager
"""
import logging
from pyqode.core.api.manager import Manager


def _logger():
    return logging.getLogger(__name__)


class TextDecorationsManager(Manager):
    def __init__(self, editor):
        super().__init__(editor)
        self._decorations = []

    def append(self, decoration):
        """
        Adds a text decoration on a CodeEdit instance

        :param editor: CodeEdit instance
        :param decoration: Text decoration
        :type decoration: pyqode.core.api.TextDecoration
        """
        # pylint: disable=protected-access
        if decoration not in self._decorations:
            self._decorations.append(decoration)
            self._decorations = sorted(
                self._decorations, key=lambda sel: sel.draw_order)
            self.editor.setExtraSelections(self._decorations)
            return True
        return False

    def remove(self, decoration):
        try:
            self._decorations.remove(decoration)
            self.editor.setExtraSelections(self._decorations)
            return True
        except ValueError:
            _logger().exception('cannot remove decoration %r', decoration)
            return False

    def clear(self):
        self._decorations[:] = []
        self.editor.setExtraSelections(self._decorations)

    def __iter__(self):
        return iter(self._decorations)

    def __len__(self):
        return len(self._decorations)
