from pyqode.core import frontend
from pyqode.core.frontend import modes

def get_mode(editor):
    return frontend.get_mode(editor, modes.CaseConverterMode)


def test_enabled(editor):
    mode = get_mode(editor)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_slots(editor):
    mode = get_mode(editor)
    mode.to_upper()
    mode.to_lower()
