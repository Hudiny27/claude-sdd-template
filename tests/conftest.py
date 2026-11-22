"""Shared fixtures for the template's tests."""

import pytest

from libtest import Repo


@pytest.fixture
def repo(tmp_path):
    """A throwaway git repo; after the test, the scripts' TMPDIR must be empty."""
    r = Repo(tmp_path)
    yield r
    assert r.leftovers() == [], "a script left files in TMPDIR"
