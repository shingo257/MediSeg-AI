"""
Main execution script for MediSeg.AI project
"""

import os
import sys
import argparse
import torch
import yaml
from pathlib import Path

# Add src to path
sys.path.append('src')

from src.models.unet import UNet
from src.data_loaders.pascal_voc import create_pascal_voc_dataloaders
from src.training.trainer import SegmentationTrainer
from src.evaluation.evaluate import ModelEvaluator


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def train_model(config_path: str, data_dir: str, save_dir: str):
    """Train U-Net model on Pascal VOC dataset"""
    print("=" * 60)
    print("MediSeg.AI - Training U-Net on Pascal VOC 2012")
    print("=" * 60)
    
    # Load configuration
    config = load_config(config_path)
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create model
    model = UNet(
        n_channels=config['model']['in_channels'],
        n_classes=config['model']['num_classes'],
        bilinear=config['model'].get('bilinear', False)
    )
    
    print(f"Model created with {sum(p.numel() for p in model.parameters()):,} parameters")
    
    # Create data loaders
    print("Creating data loaders...")
    train_loader, val_loader = create_pascal_voc_dataloaders(
        root_dir=data_dir,
        batch_size=config['data']['batch_size'],
        num_workers=config['data']['num_workers'],
        image_size=tuple(config['data']['image_size'])
    )
    
    print(f"Train samples: {len(train_loader.dataset)}")
    print(f"Validation samples: {len(val_loader.dataset)}")
    
    # Create trainer
    trainer = SegmentationTrainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        config=config,
        save_dir=save_dir
    )
    
    # Start training
    epochs = config['training']['epochs']
    print(f"Starting training for {epochs} epochs...")
    
    summary = trainer.train(epochs)
    
    print("Training completed!")
    print(f"Best Dice Score: {summary['best_dice']:.4f}")
    print(f"Final Epoch: {summary['final_epoch']}")
    
    return summary


def evaluate_model(model_path: str, data_dir: str, save_dir: str):
    """Evaluate trained model"""
    print("=" * 60)
    print("MediSeg.AI - Evaluating Trained Model")
    print("=" * 60)
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load model
    print(f"Loading model from: {model_path}")
    checkpoint = torch.load(model_path, map_location=device)
    config = checkpoint['config']
    
    model = UNet(
        n_channels=config['model']['in_channels'],
        n_classes=config['model']['num_classes'],
        bilinear=config['model'].get('bilinear', False)
    )
    model.load_state_dict(checkpoint['model_state_dict'])
    
    print(f"Model loaded with {sum(p.numel() for p in model.parameters()):,} parameters")
    
    # Create test dataset
    from src.data_loaders.pascal_voc import PascalVOCDataset, get_pascal_voc_transforms
    
    test_transform = get_pascal_voc_transforms(
        image_size=tuple(config['data']['image_size']),
        is_training=False
    )
    
    test_dataset = PascalVOCDataset(
        root_dir=data_dir,
        split='test',
        transform=test_transform
    )
    
    test_loader = torch.utils.data.DataLoader(
        test_dataset,
        batch_size=config['data']['batch_size'],
        shuffle=False,
        num_workers=config['data']['num_workers'],
        pin_memory=True
    )
    
    print(f"Test samples: {len(test_dataset)}")
    
    # Create evaluator
    evaluator = ModelEvaluator(
        model=model,
        test_loader=test_loader,
        device=device,
        save_dir=save_dir
    )
    
    # Run evaluation
    results = evaluator.evaluate()
    
    # Save results
    evaluator.save_results(results)
    
    print("Evaluation completed!")
    return results


def demo_model():
    """Demonstrate model with dummy data"""
    print("=" * 60)
    print("MediSeg.AI - Model Demonstration")
    print("=" * 60)
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create model
    model = UNet(n_channels=3, n_classes=1, bilinear=False).to(device)
    print(f"Model created with {sum(p.numel() for p in model.parameters()):,} parameters")
    
    # Test with dummy data
    print("Testing with dummy data...")
    batch_size = 2
    height, width = 256, 256
    
    # Create dummy input
    dummy_input = torch.randn(batch_size, 3, height, width).to(device)
    
    # Forward pass
    model.eval()
    with torch.no_grad():
        output = model(dummy_input)
    
    print(f"Input shape: {dummy_input.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Output range: [{output.min():.4f}, {output.max():.4f}]")
    
    # Test metrics with more realistic dummy data
    from src.evaluation.metrics import SegmentationMetrics
    
    # より現実的なダミーデータを生成
    # 予測値を0-1の範囲に正規化
    output_normalized = torch.sigmoid(output)
    
    # ターゲットも0-1の範囲で、予測値とある程度重複するように生成
    dummy_target = torch.rand(batch_size, 1, height, width).to(device)
    # ターゲットをバイナリ化（0.5を閾値として）
    dummy_target = (dummy_target > 0.5).float()
    
    metrics = SegmentationMetrics()
    metrics.update(output, dummy_target)
    results = metrics.compute()
    
    print("\nMetrics on dummy data:")
    for metric, value in results.items():
        print(f"{metric.capitalize()}: {value:.4f}")
    
    # より詳細な情報を表示
    print(f"\nDetailed analysis:")
    print(f"Target shape: {dummy_target.shape}")
    print(f"Target unique values: {torch.unique(dummy_target)}")
    print(f"Target positive ratio: {dummy_target.mean():.4f}")
    
    # 予測値の統計
    pred_binary = (torch.sigmoid(output) > 0.5).float()
    print(f"Prediction positive ratio: {pred_binary.mean():.4f}")
    print(f"Overlap ratio: {(pred_binary * dummy_target).sum() / (pred_binary + dummy_target).clamp(max=1).sum():.4f}")
    
    print("Demo completed!")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='MediSeg.AI - Medical Image Segmentation')
    parser.add_argument('--mode', type=str, 
                       choices=['train', 'eval', 'demo', 'compare', 'train_medical', 'auto_dataset', 'real_datasets', 'gui'], 
                       default='demo', help='Execution mode')
    parser.add_argument('--config', type=str, default='configs/base_config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--data_dir', type=str, default='data/pascal_voc',
                       help='Path to dataset directory')
    parser.add_argument('--save_dir', type=str, default='results',
                       help='Directory to save results')
    parser.add_argument('--model_path', type=str, default='results/best_model.pth',
                       help='Path to trained model for evaluation')
    parser.add_argument('--dataset', type=str, choices=['pascal_voc', 'isic'], 
                       default='pascal_voc', help='Dataset to use')
    
    args = parser.parse_args()
    
    if args.mode == 'train':
        from src.cli.commands.train_command import TrainCommand
        TrainCommand.execute(args.config, args.data_dir, args.save_dir)
    
    elif args.mode == 'train_medical':
        if not os.path.exists(args.data_dir):
            print(f"Error: Data directory {args.data_dir} does not exist")
            print("Please download ISIC dataset first")
            return
        
        # Use medical config for ISIC dataset
        config_path = 'configs/isic_config.yaml'
        from src.cli.commands.train_command import TrainCommand
        TrainCommand.execute(config_path, args.data_dir, args.save_dir)
    
    elif args.mode == 'eval':
        from src.cli.commands.eval_command import EvalCommand
        EvalCommand.execute(args.model_path, args.data_dir, args.save_dir)
    
    elif args.mode == 'compare':
        from src.cli.commands.compare_command import CompareCommand
        CompareCommand.execute(args.dataset, args.data_dir, args.save_dir)
    
    elif args.mode == 'demo':
        from src.cli.commands.demo_command import DemoCommand
        DemoCommand.execute()
    
    elif args.mode == 'auto_dataset':
        from src.cli.commands.dataset_command import DatasetCommand
        DatasetCommand.execute('auto')
    
    elif args.mode == 'real_datasets':
        from src.cli.commands.dataset_command import DatasetCommand
        DatasetCommand.execute('real')
    
    elif args.mode == 'gui':
        print("🎨 Launching MediSeg.AI Web GUI...")
        try:
            from src.gui.launcher import WebGUILauncher
            launcher = WebGUILauncher()
            launcher.launch()
        except ImportError as e:
            print(f"❌ Failed to import Web GUI: {e}")
            print("Please install Web GUI dependencies:")
            print("pip install flask torch opencv-python matplotlib seaborn pillow")
        except Exception as e:
            print(f"❌ Failed to start Web GUI: {e}")
            print("Try running: python web_gui_launcher.py")


if __name__ == "__main__":
    main()
