"""
Evaluation metrics for medical image segmentation
"""

import torch
import torch.nn.functional as F
import numpy as np
from typing import Union, List


def dice_coefficient(pred: torch.Tensor, target: torch.Tensor, smooth: float = 1e-6) -> torch.Tensor:
    """
    Calculate Dice coefficient between prediction and target
    
    Args:
        pred: Predicted segmentation mask
        target: Ground truth segmentation mask
        smooth: Smoothing factor to avoid division by zero
        
    Returns:
        Dice coefficient
    """
    pred = torch.sigmoid(pred)
    pred = (pred > 0.5).float()
    
    intersection = (pred * target).sum()
    dice = (2. * intersection + smooth) / (pred.sum() + target.sum() + smooth)
    
    return dice


def intersection_over_union(pred: torch.Tensor, target: torch.Tensor, smooth: float = 1e-6) -> torch.Tensor:
    """
    Calculate Intersection over Union (IoU) between prediction and target
    
    Args:
        pred: Predicted segmentation mask
        target: Ground truth segmentation mask
        smooth: Smoothing factor to avoid division by zero
        
    Returns:
        IoU score
    """
    pred = torch.sigmoid(pred)
    pred = (pred > 0.5).float()
    
    intersection = (pred * target).sum()
    union = pred.sum() + target.sum() - intersection
    iou = (intersection + smooth) / (union + smooth)
    
    return iou


def pixel_accuracy(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """
    Calculate pixel-wise accuracy
    
    Args:
        pred: Predicted segmentation mask
        target: Ground truth segmentation mask
        
    Returns:
        Pixel accuracy
    """
    pred = torch.sigmoid(pred)
    pred = (pred > 0.5).float()
    
    correct = (pred == target).float().sum()
    total = target.numel()
    
    return correct / total


def sensitivity(pred: torch.Tensor, target: torch.Tensor, smooth: float = 1e-6) -> torch.Tensor:
    """
    Calculate sensitivity (recall) for binary segmentation
    
    Args:
        pred: Predicted segmentation mask
        target: Ground truth segmentation mask
        smooth: Smoothing factor to avoid division by zero
        
    Returns:
        Sensitivity score
    """
    pred = torch.sigmoid(pred)
    pred = (pred > 0.5).float()
    
    true_positives = (pred * target).sum()
    false_negatives = (target * (1 - pred)).sum()
    
    sensitivity = (true_positives + smooth) / (true_positives + false_negatives + smooth)
    
    return sensitivity


def specificity(pred: torch.Tensor, target: torch.Tensor, smooth: float = 1e-6) -> torch.Tensor:
    """
    Calculate specificity for binary segmentation
    
    Args:
        pred: Predicted segmentation mask
        target: Ground truth segmentation mask
        smooth: Smoothing factor to avoid division by zero
        
    Returns:
        Specificity score
    """
    pred = torch.sigmoid(pred)
    pred = (pred > 0.5).float()
    
    true_negatives = ((1 - pred) * (1 - target)).sum()
    false_positives = (pred * (1 - target)).sum()
    
    specificity = (true_negatives + smooth) / (true_negatives + false_positives + smooth)
    
    return specificity


class SegmentationMetrics:
    """
    Comprehensive metrics calculator for segmentation tasks
    """
    
    def __init__(self, num_classes: int = 1):
        self.num_classes = num_classes
        self.reset()
    
    def reset(self):
        """Reset all metrics"""
        self.dice_scores = []
        self.iou_scores = []
        self.accuracy_scores = []
        self.sensitivity_scores = []
        self.specificity_scores = []
    
    def update(self, pred: torch.Tensor, target: torch.Tensor):
        """
        Update metrics with new predictions and targets
        
        Args:
            pred: Predicted segmentation masks
            target: Ground truth segmentation masks
        """
        batch_size = pred.shape[0]
        
        for i in range(batch_size):
            pred_i = pred[i]
            target_i = target[i]
            
            self.dice_scores.append(dice_coefficient(pred_i, target_i).item())
            self.iou_scores.append(intersection_over_union(pred_i, target_i).item())
            self.accuracy_scores.append(pixel_accuracy(pred_i, target_i).item())
            self.sensitivity_scores.append(sensitivity(pred_i, target_i).item())
            self.specificity_scores.append(specificity(pred_i, target_i).item())
    
    def compute(self) -> dict:
        """
        Compute final metrics
        
        Returns:
            Dictionary containing all computed metrics
        """
        return {
            'dice': np.mean(self.dice_scores),
            'iou': np.mean(self.iou_scores),
            'accuracy': np.mean(self.accuracy_scores),
            'sensitivity': np.mean(self.sensitivity_scores),
            'specificity': np.mean(self.specificity_scores)
        }
    
    def get_summary(self) -> str:
        """
        Get a formatted summary of all metrics
        
        Returns:
            Formatted string with metrics summary
        """
        metrics = self.compute()
        summary = "Segmentation Metrics Summary:\n"
        summary += f"Dice Coefficient: {metrics['dice']:.4f}\n"
        summary += f"IoU: {metrics['iou']:.4f}\n"
        summary += f"Pixel Accuracy: {metrics['accuracy']:.4f}\n"
        summary += f"Sensitivity: {metrics['sensitivity']:.4f}\n"
        summary += f"Specificity: {metrics['specificity']:.4f}\n"
        return summary


def test_metrics():
    """Test function for metrics"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Create test data
    pred = torch.randn(2, 1, 64, 64).to(device)
    target = torch.randint(0, 2, (2, 1, 64, 64)).float().to(device)
    
    # Test individual metrics
    dice = dice_coefficient(pred, target)
    iou = intersection_over_union(pred, target)
    acc = pixel_accuracy(pred, target)
    
    print(f"Dice Coefficient: {dice:.4f}")
    print(f"IoU: {iou:.4f}")
    print(f"Pixel Accuracy: {acc:.4f}")
    
    # Test comprehensive metrics
    metrics = SegmentationMetrics()
    metrics.update(pred, target)
    print(metrics.get_summary())


if __name__ == "__main__":
    test_metrics()
