"""
Pytest configuration for HDL-FSM-Editor tests.
"""

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent.resolve()


@pytest.fixture(scope="session")
def test_output_dir(project_root):
    """Get the test output directory."""
    output_dir = project_root / "tests" / "test_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir
