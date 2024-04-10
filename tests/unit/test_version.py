"""This module tests the ska_ser_test_equipment version."""

import ska_mid_jupyter_scripting


def test_version() -> None:
    """Test that the ska_mid_jupyter_scripting version is as expected."""
    assert ska_mid_jupyter_scripting.__version__ == "0.1.0"
