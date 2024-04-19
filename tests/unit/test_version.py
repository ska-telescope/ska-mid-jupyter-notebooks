"""This module tests the ska_ser_test_equipment version."""

import ska_mid_jupyter_notebooks


def test_version() -> None:
    """Test that the ska_mid_jupyter_notebooks version is as expected."""
    assert ska_mid_jupyter_notebooks.__version__ == "0.1.0"
