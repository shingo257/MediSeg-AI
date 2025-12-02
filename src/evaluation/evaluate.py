"""
Evaluation script for trained segmentation models
"""

import os
import sys
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, List
import argparse
from tqdm import tqdm

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.unet import UNet
from data_loaders.pascal_voc import PascalVOCDataset, get_pascal_voc_transforms
from evaluation.metrics import SegmentationMetrics


class ModelEvaluator:
    """
    Evaluator class for segmentation models
    """
    
    def __init__(
        self,
        model: nn.Module,
        test_loader: torch.utils.data.DataLoader,
        device: torch.device,
        save_dir: str = "results"
    ):
        self.model = model.to(device)
        self.test_loader = test_loader
        self.device = device
        self.save_dir = save_dir
        
        # Create save directory
        os.makedirs(save_dir, exist_ok=True)
        
        # Evaluation metrics
        self.metrics = SegmentationMetrics()
        self.predictions = []
        self.targets = []
        self.images = []
    
    def evaluate(self) -> Dict[str, float]:
        """
        Evaluate the model on test dataset
        
        Returns:
            Dictionary containing evaluation metrics
        """
        self.model.eval()
        self.metrics.reset()
        
        print("Evaluating model...")
        
        with torch.no_grad():
            for batch_idx, (images, targets) in enumerate(tqdm(self.test_loader)):
                images = images.to(self.device)
                targets = targets.to(self.device)
                
                # Forward pass
                outputs = self.model(images)
                
                # Update metrics
                self.metrics.update(outputs, targets)
                
                # Store for visualization
                if batch_idx < 10:  # Store first 10 batches for visualization
                    self.predictions.append(outputs.cpu())
                    self.targets.append(targets.cpu())
                    self.images.append(images.cpu())
        
        # Compute final metrics
        results = self.metrics.compute()
        
        print("Evaluation Results:")
        print(f"Dice Coefficient: {results['dice']:.4f}")
        print(f"IoU: {results['iou']:.4f}")
        print(f"Pixel Accuracy: {results['accuracy']:.4f}")
        print(f"Sensitivity: {results['sensitivity']:.4f}")
        print(f"Specificity: {results['specificity']:.4f}")
        
        return results
    
    def visualize_predictions(self, num_samples: int = 8) -> None:
        """
        Visualize model predictions
        
        Args:
            num_samples: Number of samples to visualize
        """
        if not self.predictions:
            print("No predictions available for visualization")
            return
        
        # Flatten predictions and targets
        all_predictions = torch.cat(self.predictions, dim=0)
        all_targets = torch.cat(self.targets, dim=0)
        all_images = torch.cat(self.images, dim=0)
        
        # Select random samples
        indices = torch.randperm(len(all_images))[:num_samples]
        
        # Create visualization
        fig, axes = plt.subplots(3, num_samples, figsize=(2 * num_samples, 6))
        
        for i, idx in enumerate(indices):
            # Original image
            img = all_images[idx].permute(1, 2, 0)
            img = (img - img.min()) / (img.max() - img.min())
            axes[0, i].imshow(img)
            axes[0, i].set_title(f'Image {idx.item()}')
            axes[0, i].axis('off')
            
            # Ground truth
            gt = all_targets[idx].squeeze()
            axes[1, i].imshow(gt, cmap='gray')
            axes[1, i].set_title(f'Ground Truth {idx.item()}')
            axes[1, i].axis('off')
            
            # Prediction
            pred = torch.sigmoid(all_predictions[idx]).squeeze()
            axes[2, i].imshow(pred, cmap='gray')
            axes[2, i].set_title(f'Prediction {idx.item()}')
            axes[2, i].axis('off')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.save_dir, 'predictions_visualization.png'), 
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    def save_results(self, results: Dict[str, float]) -> None:
        """
        Save evaluation results to file
        
        Args:
            results: Dictionary containing evaluation metrics
        """
        results_file = os.path.join(self.save_dir, 'evaluation_results.txt')
        
        with open(results_file, 'w') as f:
            f.write("Evaluation Results\n")
            f.write("=" * 50 + "\n")
            for metric, value in results.items():
                f.write(f"{metric.capitalize()}: {value:.4f}\n")
        
        print(f"Results saved to: {results_file}")


def load_model(model_path: str, config: Dict[str, Any], device: torch.device) -> nn.Module:
    """
    Load trained model from checkpoint
    
    Args:
        model_path: Path to model checkpoint
        config: Model configuration
        device: Device to load model on
        
    Returns:
        Loaded model
    """
    # Create model
    model = UNet(
        n_channels=config['model']['in_channels'],
        n_classes=config['model']['num_classes'],
        bilinear=config['model'].get('bilinear', False)
    )
    
    # Load checkpoint
    checkpoint = torch.load(model_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    
    return model


def main():
    """Main evaluation function"""
    parser = argparse.ArgumentParser(description='Evaluate trained U-Net model')
    parser.add_argument('--model_path', type=str, required=True,
                       help='Path to trained model checkpoint')
    parser.add_argument('--data_dir', type=str, required=True,
                       help='Path to Pascal VOC 2012 dataset')
    parser.add_argument('--save_dir', type=str, default='results',
                       help='Directory to save evaluation results')
    parser.add_argument('--batch_size', type=int, default=16,
                       help='Batch size for evaluation')
    parser.add_argument('--num_workers', type=int, default=4,
                       help='Number of worker processes')
    parser.add_argument('--visualize', action='store_true',
                       help='Generate visualization plots')
    
    args = parser.parse_args()
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load model
    print(f"Loading model from: {args.model_path}")
    checkpoint = torch.load(args.model_path, map_location=device)
    config = checkpoint['config']
    
    model = load_model(args.model_path, config, device)
    print(f"Model loaded with {sum(p.numel() for p in model.parameters()):,} parameters")
    
    # Create test dataset
    print("Creating test dataset...")
    test_transform = get_pascal_voc_transforms(
        image_size=tuple(config['data']['image_size']),
        is_training=False
    )
    
    test_dataset = PascalVOCDataset(
        root_dir=args.data_dir,
        split='test',
        transform=test_transform
    )
    
    test_loader = torch.utils.data.DataLoader(
        test_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=True
    )
    
    print(f"Test samples: {len(test_dataset)}")
    
    # Create evaluator
    evaluator = ModelEvaluator(
        model=model,
        test_loader=test_loader,
        device=device,
        save_dir=args.save_dir
    )
    
    # Run evaluation
    results = evaluator.evaluate()
    
    # Save results
    evaluator.save_results(results)
    
    # Generate visualizations
    if args.visualize:
        print("Generating visualizations...")
        evaluator.visualize_predictions()
    
    print("Evaluation completed!")


if __name__ == "__main__":
    main()
