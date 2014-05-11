# -*- coding: utf-8 -*-
"""
This module tests the extension frontend module
(pyqode.core.frontend.extension)
"""
from PyQt4.QtTest import QTest

import pytest
from pyqode.core import frontend
from ..helpers import editor_open
from ..helpers import log_test_name
from ..helpers import preserve_editor_config


@editor_open(__file__)
@preserve_editor_config
@log_test_name
def test_modes(editor):
    """
    Test to install, retrieve and remove a mode.

    """
    from pyqode.core.frontend.modes import CaseConverterMode
    frontend.uninstall_all(editor)
    mode = CaseConverterMode()
    frontend.install_mode(editor, mode)
    m = frontend.get_mode(editor, CaseConverterMode)
    assert len(frontend.get_modes(editor)) == 1
    assert m == mode
    m = frontend.uninstall_mode(editor, CaseConverterMode)
    assert m == mode
    with pytest.raises(KeyError):
        frontend.uninstall_mode(editor, CaseConverterMode)

@editor_open(__file__)
@log_test_name
@preserve_editor_config
def test_panels(editor):
    """
    Test to install, retrieve and remove a panel

    """
    from pyqode.core.frontend.panels import LineNumberPanel
    panel = LineNumberPanel()
    frontend.install_panel(editor, panel, panel.Position.LEFT)
    QTest.qWait(1000)
    p, zone = frontend.get_panel(editor, LineNumberPanel, get_zone=True)
    p2 = frontend.get_panel(editor, LineNumberPanel, get_zone=False)
    assert p == panel == p2
    assert zone == panel.Position.LEFT
    assert len(frontend.get_panels(editor)) == 4
    for i in range(4):
        p.enabled = not p.enabled
    p = frontend.uninstall_panel(editor, LineNumberPanel)
    assert p == panel
    with pytest.raises(KeyError):
        frontend.uninstall_panel(editor, LineNumberPanel)


@editor_open(__file__)
@log_test_name
@preserve_editor_config
def test_uninstall_all(editor):
    frontend.uninstall_all(editor)
    from pyqode.core.frontend.modes import CaseConverterMode
    from pyqode.core.frontend.panels import LineNumberPanel
    mode = CaseConverterMode()
    frontend.install_mode(editor, mode)
    frontend.install_panel(editor, LineNumberPanel(),
                           LineNumberPanel.Position.LEFT)
