"""Global fixtures for the modern pytest suite."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def test_files_dir() -> Path:
    """Return absolute path to legacy shared binary/XML test assets."""
    return Path(__file__).resolve().parents[1] / "tests" / "test_files"
