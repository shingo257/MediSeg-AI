"""Test Web GUI services (create_visualization with empty/partial metrics)."""
import base64
import pytest
import numpy as np

pytest.importorskip("matplotlib")
from backend.gui.web.services import create_visualization


def test_create_visualization_with_empty_metrics_does_not_raise():
    """create_visualization with metrics={} does not raise KeyError; returns base64 string."""
    image = np.zeros((64, 64, 3), dtype=np.uint8)
    prediction = np.zeros((64, 64), dtype=np.float64)
    mask = np.zeros((64, 64), dtype=np.uint8)
    metrics = {}
    result = create_visualization(image, prediction, mask, metrics)
    assert isinstance(result, str)
    assert len(result) > 0
    raw = base64.b64decode(result)
    assert raw[:8] == b"\x89PNG\r\n\x1a\n"


def test_create_visualization_with_partial_metrics_does_not_raise():
    """create_visualization with only some metric keys uses defaults for missing ones."""
    image = np.zeros((64, 64, 3), dtype=np.uint8)
    prediction = np.zeros((64, 64), dtype=np.float64)
    mask = np.zeros((64, 64), dtype=np.uint8)
    metrics = {"dice": 0.5, "model_type": "U-Net"}
    result = create_visualization(image, prediction, mask, metrics)
    assert isinstance(result, str)
    assert len(result) > 0
