"""Test get_default_base_config and get_default_isic_config."""
import pytest
from mediseg_ai.config import get_default_base_config, get_default_isic_config


def test_get_default_base_config_returns_dict_with_expected_keys():
    """get_default_base_config returns dict with data, training, evaluation."""
    config = get_default_base_config()
    assert isinstance(config, dict)
    assert "data" in config
    assert "training" in config
    assert "evaluation" in config
    assert config["data"].get("batch_size") == 16
    assert config["training"].get("epochs") == 100
    assert config["training"].get("scheduler") == "cosine"
    assert "metrics" in config["evaluation"]
    assert "iou" in config["evaluation"]["metrics"]
    assert "dice" in config["evaluation"]["metrics"]


def test_get_default_isic_config_returns_dict_with_expected_keys():
    """get_default_isic_config returns dict with training, evaluation for ISIC."""
    config = get_default_isic_config()
    assert isinstance(config, dict)
    assert "data" in config
    assert "training" in config
    assert "evaluation" in config
    assert config["training"].get("epochs") == 150
    assert config["training"].get("loss") == "combined"
    assert "sensitivity" in config["evaluation"]["metrics"]
    assert "specificity" in config["evaluation"]["metrics"]


def test_get_default_base_config_returns_fresh_copy_each_time():
    """Each call returns a new dict; mutating one does not affect another."""
    a = get_default_base_config()
    b = get_default_base_config()
    a["data"]["batch_size"] = 999
    assert b["data"]["batch_size"] == 16
