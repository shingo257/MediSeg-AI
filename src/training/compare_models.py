"""
Model comparison script for U-Net vs DeepLabV3+
"""

import os
import sys
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
import time
import argparse

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.unet import UNet
from models.deeplabv3plus import create_deeplabv3plus
from evaluation.metrics import SegmentationMetrics
from data_loaders.pascal_voc import create_pascal_voc_dataloaders
from data_loaders.isic import create_isic_dataloaders


class ModelComparator:
    """
    Compare different segmentation models
    """
    
    def __init__(self, device: torch.device):
        self.device = device
        self.results = {}
    
    def create_models(self) -> Dict[str, nn.Module]:
        """Create different models for comparison"""
        models = {}
        
        # U-Net
        models['unet'] = UNet(n_channels=3, n_classes=1, bilinear=False).to(self.device)
        
        # DeepLabV3+
        models['deeplabv3plus'] = create_deeplabv3plus(
            num_classes=1, 
            backbone='resnet50', 
            pretrained=False
        ).to(self.device)
        
        return models
    
    def evaluate_model(
        self, 
        model: nn.Module, 
        dataloader: torch.utils.data.DataLoader,
        model_name: str
    ) -> Dict[str, float]:
        """Evaluate a single model"""
        model.eval()
        metrics = SegmentationMetrics()
        total_time = 0.0
        num_samples = 0
        
        print(f"Evaluating {model_name}...")
        
        with torch.no_grad():
            for images, targets in dataloader:
                images = images.to(self.device)
                targets = targets.to(self.device)
                
                # Measure inference time
                start_time = time.time()
                outputs = model(images)
                end_time = time.time()
                
                total_time += (end_time - start_time)
                num_samples += images.shape[0]
                
                # Update metrics
                metrics.update(outputs, targets)
        
        # Calculate results
        results = metrics.compute()
        results['inference_time'] = total_time / num_samples  # seconds per sample
        results['throughput'] = num_samples / total_time  # samples per second
        
        print(f"{model_name} Results:")
        print(f"  Dice: {results['dice']:.4f}")
        print(f"  IoU: {results['iou']:.4f}")
        print(f"  Accuracy: {results['accuracy']:.4f}")
        print(f"  Inference Time: {results['inference_time']:.4f}s per sample")
        print(f"  Throughput: {results['throughput']:.2f} samples/s")
        
        return results
    
    def compare_models(
        self, 
        dataloader: torch.utils.data.DataLoader,
        dataset_name: str
    ) -> Dict[str, Dict[str, float]]:
        """Compare all models on the given dataset"""
        print(f"\n{'='*60}")
        print(f"Comparing models on {dataset_name} dataset")
        print(f"{'='*60}")
        
        models = self.create_models()
        results = {}
        
        for model_name, model in models.items():
            # Count parameters
            num_params = sum(p.numel() for p in model.parameters())
            model_size = num_params * 4 / 1024 / 1024  # MB
            
            print(f"\n{model_name.upper()}:")
            print(f"  Parameters: {num_params:,}")
            print(f"  Model Size: {model_size:.2f} MB")
            
            # Evaluate model
            model_results = self.evaluate_model(model, dataloader, model_name)
            model_results['num_parameters'] = num_params
            model_results['model_size_mb'] = model_size
            
            results[model_name] = model_results
        
        return results
    
    def create_comparison_plot(self, results: Dict[str, Dict[str, float]], save_path: str):
        """Create comparison plots"""
        models = list(results.keys())
        metrics = ['dice', 'iou', 'accuracy', 'inference_time']
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        axes = axes.flatten()
        
        for i, metric in enumerate(metrics):
            values = [results[model][metric] for model in models]
            
            bars = axes[i].bar(models, values, alpha=0.7)
            axes[i].set_title(f'{metric.upper()} Comparison')
            axes[i].set_ylabel(metric.upper())
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                axes[i].text(bar.get_x() + bar.get_width()/2., height,
                           f'{value:.4f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_summary_table(self, results: Dict[str, Dict[str, float]]) -> str:
        """Create a summary table of results"""
        table = "\n" + "="*80 + "\n"
        table += "MODEL COMPARISON SUMMARY\n"
        table += "="*80 + "\n"
        
        # Header
        table += f"{'Model':<15} {'Dice':<8} {'IoU':<8} {'Acc':<8} {'Time(s)':<10} {'Params(M)':<12} {'Size(MB)':<10}\n"
        table += "-"*80 + "\n"
        
        # Data rows
        for model_name, result in results.items():
            table += f"{model_name:<15} "
            table += f"{result['dice']:<8.4f} "
            table += f"{result['iou']:<8.4f} "
            table += f"{result['accuracy']:<8.4f} "
            table += f"{result['inference_time']:<10.4f} "
            table += f"{result['num_parameters']/1e6:<12.2f} "
            table += f"{result['model_size_mb']:<10.2f}\n"
        
        table += "="*80 + "\n"
        
        return table


def main():
    """Main comparison function"""
    parser = argparse.ArgumentParser(description='Compare segmentation models')
    parser.add_argument('--dataset', type=str, choices=['pascal_voc', 'isic'], 
                       default='pascal_voc', help='Dataset to use for comparison')
    parser.add_argument('--data_dir', type=str, required=True,
                       help='Path to dataset directory')
    parser.add_argument('--save_dir', type=str, default='results',
                       help='Directory to save comparison results')
    parser.add_argument('--batch_size', type=int, default=8,
                       help='Batch size for evaluation')
    
    args = parser.parse_args()
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create save directory
    os.makedirs(args.save_dir, exist_ok=True)
    
    # Create comparator
    comparator = ModelComparator(device)
    
    # Create dataloader
    if args.dataset == 'pascal_voc':
        _, _, test_loader = create_pascal_voc_dataloaders(
            root_dir=args.data_dir,
            batch_size=args.batch_size,
            num_workers=2
        )
    elif args.dataset == 'isic':
        _, _, test_loader = create_isic_dataloaders(
            root_dir=args.data_dir,
            batch_size=args.batch_size,
            num_workers=2
        )
    
    print(f"Test samples: {len(test_loader.dataset)}")
    
    # Compare models
    results = comparator.compare_models(test_loader, args.dataset)
    
    # Create comparison plot
    plot_path = os.path.join(args.save_dir, f'model_comparison_{args.dataset}.png')
    comparator.create_comparison_plot(results, plot_path)
    
    # Create summary table
    summary = comparator.create_summary_table(results)
    print(summary)
    
    # Save results
    results_file = os.path.join(args.save_dir, f'comparison_results_{args.dataset}.txt')
    with open(results_file, 'w') as f:
        f.write(summary)
    
    print(f"Results saved to: {results_file}")
    print(f"Comparison plot saved to: {plot_path}")


if __name__ == "__main__":
    main()
