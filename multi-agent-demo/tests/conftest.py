"""Pytest fixtures."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from manus_agent.config.settings import Settings


@pytest.fixture
def tmp_settings() -> Settings:
    with tempfile.TemporaryDirectory() as tmp:
        yield Settings(llm_provider="mock", data_dir=Path(tmp))
