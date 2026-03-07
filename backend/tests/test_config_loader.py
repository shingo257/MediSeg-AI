"""Test ConfigLoader.ensure_config and load_yaml."""
import os
import tempfile
from pathlib import Path
import pytest
from mediseg_ai.utils.common import ConfigLoader


def test_ensure_config_creates_file_and_returns_content():
    """ConfigLoader.ensure_config creates YAML from default_template when path does not exist."""
    default_template = {
        "data": {"batch_size": 16, "num_workers": 4},
        "model": {"name": "unet", "num_classes": 1},
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "subdir", "config.yaml")
        result = ConfigLoader.ensure_config(config_path, default_template)
        assert result == default_template
        assert Path(config_path).exists()
        # Read back raw and verify structure
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "batch_size" in content
        assert "unet" in content


def test_ensure_config_uses_existing_file():
    """ConfigLoader.ensure_config returns existing file content when path exists."""
    existing_config = {"data": {"batch_size": 8}, "model": {"name": "custom"}}
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "existing.yaml")
        import yaml
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(existing_config, f, default_flow_style=False, allow_unicode=True)
        default_template = {"data": {"batch_size": 16}}
        result = ConfigLoader.ensure_config(config_path, default_template)
        assert result["data"]["batch_size"] == 8
        assert result["model"]["name"] == "custom"


def test_load_yaml_raises_when_file_not_found():
    """ConfigLoader.load_yaml raises FileNotFoundError when path does not exist."""
    with pytest.raises(FileNotFoundError, match="Config file not found"):
        ConfigLoader.load_yaml("/nonexistent/path/config.yaml")
