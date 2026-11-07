from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from idata.idata_gui import InfoDataGui


@pytest.mark.parametrize(
    ("axes", "overrides", "expected_labels", "expected_calls"),
    [
        ({"i": "Time tick"}, {}, ("Time tick", "None"), ["i"]),
        ({"x": "X axis", "y": "Y axis"}, {}, ("X axis", "Y axis"), ["x", "y"]),
        ({}, {}, ("None", "None"), []),
        ({"i": "Time tick"}, {"keyX": "None", "keyY": "None"}, ("None", "None"), []),
    ],
)
def test_update_display_bar_handles_missing_axes(axes, overrides, expected_labels, expected_calls):
    data = MagicMock()
    data.getSchemaAxes.return_value = axes
    data.getSchemaVals.return_value = {"v": {"name": "Value"}}
    data.axeNameByKey.side_effect = axes.__getitem__
    gui = SimpleNamespace(
        data=data,
        name="test GUI",
        sub2D={},
        lblX={},
        lblY={},
        cbValName=MagicMock(),
    )

    InfoDataGui.resetDisplay(gui)
    gui.display.update(overrides)
    InfoDataGui.updateDisplayBar(gui)

    assert (gui.lblX["text"], gui.lblY["text"]) == expected_labels
    assert [call.args[0] for call in data.axeNameByKey.call_args_list] == expected_calls
    gui.cbValName.set.assert_called_once_with("Value")
