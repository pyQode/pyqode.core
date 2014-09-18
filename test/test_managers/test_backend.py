from ..helpers import editor_open


@editor_open(__file__)
def test_exit_code(editor):
    assert editor.backend.connected
    assert editor.backend.exit_code is None
    editor.backend.stop()
    assert not editor.backend.connected
    assert editor.backend.exit_code == 0
