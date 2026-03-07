"""Tests for evaluation metrics (dice, IoU, pixel accuracy, SegmentationMetrics)."""
import pytest
import torch
from mediseg_ai.evaluation.metrics import (
    dice_coefficient,
    intersection_over_union,
    pixel_accuracy,
    sensitivity,
    specificity,
    SegmentationMetrics,
)


@pytest.fixture
def dummy_tensors():
    """Binary prediction logits and target masks; batch=2, 1 channel, 4x4."""
    pred = torch.randn(2, 1, 4, 4)
    target = (torch.rand(2, 1, 4, 4) > 0.5).float()
    return pred, target


def test_dice_coefficient_shape_and_range(dummy_tensors):
    pred, target = dummy_tensors
    dice = dice_coefficient(pred, target)
    assert dice.dim() == 0
    assert 0.0 <= dice.item() <= 1.0


def test_dice_coefficient_perfect_match():
    pred = torch.tensor([[[[100.0]]]])  # sigmoid ~ 1
    target = torch.ones(1, 1, 1, 1)
    dice = dice_coefficient(pred, target)
    assert dice.item() > 0.99


def test_intersection_over_union_shape_and_range(dummy_tensors):
    pred, target = dummy_tensors
    iou = intersection_over_union(pred, target)
    assert iou.dim() == 0
    assert 0.0 <= iou.item() <= 1.0


def test_pixel_accuracy_shape_and_range(dummy_tensors):
    pred, target = dummy_tensors
    acc = pixel_accuracy(pred, target)
    assert acc.dim() == 0
    assert 0.0 <= acc.item() <= 1.0


def test_sensitivity_shape_and_range(dummy_tensors):
    pred, target = dummy_tensors
    sens = sensitivity(pred, target)
    assert sens.dim() == 0
    assert 0.0 <= sens.item() <= 1.0


def test_specificity_shape_and_range(dummy_tensors):
    pred, target = dummy_tensors
    spec = specificity(pred, target)
    assert spec.dim() == 0
    assert 0.0 <= spec.item() <= 1.0


def test_segmentation_metrics_update_and_compute(dummy_tensors):
    pred, target = dummy_tensors
    metrics = SegmentationMetrics(num_classes=1)
    metrics.update(pred, target)
    result = metrics.compute()
    assert "dice" in result
    assert "iou" in result
    assert "accuracy" in result
    assert "sensitivity" in result
    assert "specificity" in result
    for v in result.values():
        assert 0.0 <= v <= 1.0


def test_segmentation_metrics_reset(dummy_tensors):
    pred, target = dummy_tensors
    metrics = SegmentationMetrics()
    metrics.update(pred, target)
    metrics.reset()
    out = metrics.compute()
    assert "dice" in out
    assert "iou" in out
    # After reset, lists are empty; np.mean([]) is nan
    import math
    assert math.isnan(out["dice"]) or out["dice"] == 0.0
    assert math.isnan(out["iou"]) or out["iou"] == 0.0


def test_segmentation_metrics_get_summary(dummy_tensors):
    pred, target = dummy_tensors
    metrics = SegmentationMetrics()
    metrics.update(pred, target)
    summary = metrics.get_summary()
    assert "Dice" in summary
    assert "IoU" in summary
    assert "Accuracy" in summary
