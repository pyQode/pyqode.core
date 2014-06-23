from pyqode.core import modes


def get_mode(editor):
    return editor.modes.get(modes.CaseConverterMode)


def test_enabled(editor):
    mode = get_mode(editor)
    assert mode.enabled
    mode.enabled = False
    mode.enabled = True


def test_slots(editor):
    mode = get_mode(editor)
    mode.to_upper()
    mode.to_lower()
