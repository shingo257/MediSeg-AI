"""
Training script for U-Net on Pascal VOC 2012 dataset
"""

import os
import sys
import yaml
import argparse
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.unet import UNet
from data_loaders.pascal_voc import create_pascal_voc_dataloaders
from training.trainer import SegmentationTrainer


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def create_model(config: dict) -> nn.Module:
    """Create U-Net model based on configuration"""
    model_config = config['model']
    
    model = UNet(
        n_channels=model_config.get('in_channels', 3),
        n_classes=model_config.get('num_classes', 1),
        bilinear=model_config.get('bilinear', False)
    )
    
    return model


def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description='Train U-Net on Pascal VOC 2012')
    parser.add_argument('--config', type=str, default='configs/base_config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--data_dir', type=str, required=True,
                       help='Path to Pascal VOC 2012 dataset')
    parser.add_argument('--save_dir', type=str, default='results',
                       help='Directory to save results')
    parser.add_argument('--resume', type=str, default=None,
                       help='Path to checkpoint to resume from')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create model
    model = create_model(config)
    print(f"Model created with {sum(p.numel() for p in model.parameters()):,} parameters")
    
    # Create data loaders
    print("Creating data loaders...")
    train_loader, val_loader = create_pascal_voc_dataloaders(
        root_dir=args.data_dir,
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
        save_dir=args.save_dir
    )
    
    # Resume from checkpoint if specified
    if args.resume:
        print(f"Resuming from checkpoint: {args.resume}")
        checkpoint = torch.load(args.resume, map_location=device)
        trainer.model.load_state_dict(checkpoint['model_state_dict'])
        trainer.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        if trainer.scheduler and checkpoint['scheduler_state_dict']:
            trainer.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        trainer.current_epoch = checkpoint['epoch']
        trainer.best_dice = checkpoint['metrics']['dice']
    
    # Start training
    epochs = config['training']['epochs']
    print(f"Starting training for {epochs} epochs...")
    
    summary = trainer.train(epochs)
    
    print("Training completed!")
    print(f"Best Dice Score: {summary['best_dice']:.4f}")
    print(f"Final Epoch: {summary['final_epoch']}")
    
    # Save final model
    final_model_path = os.path.join(args.save_dir, 'final_model.pth')
    torch.save({
        'model_state_dict': model.state_dict(),
        'config': config,
        'summary': summary
    }, final_model_path)
    print(f"Final model saved to: {final_model_path}")


if __name__ == "__main__":
    main()
