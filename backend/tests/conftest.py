"""Pytest configuration. Ensures repo root is on path when running from backend/tests."""
import os
import sys

import pytest

# Add repo root (parent of backend) so that "backend" and installed package are importable
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)


@pytest.fixture(scope="module")
def web_app():
    """Flask app for Web GUI smoke tests. Skips if gui-web deps unavailable."""
    pytest.importorskip("flask")
    pytest.importorskip("torch")
    from backend.gui.web.web_gui import app
    app.config["TESTING"] = True
    return app
