"""
Training utilities for medical image segmentation
"""

import torch
import torch.nn as nn
import torch.optim as optim
# from torch.utils.tensorboard import SummaryWriter  # TensorBoardを無効化
import wandb
import os
import time
from typing import Dict, Any, Optional, Tuple
import numpy as np
from tqdm import tqdm

from ..evaluation.metrics import SegmentationMetrics


class SegmentationTrainer:
    """
    Trainer class for semantic segmentation models
    """
    
    def __init__(
        self,
        model: nn.Module,
        train_loader: torch.utils.data.DataLoader,
        val_loader: torch.utils.data.DataLoader,
        device: torch.device,
        config: Dict[str, Any],
        save_dir: str = "results"
    ):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        self.config = config
        self.save_dir = save_dir
        
        # Create save directory
        os.makedirs(save_dir, exist_ok=True)
        
        # Initialize optimizer and scheduler
        self.optimizer = self._setup_optimizer()
        self.scheduler = self._setup_scheduler()
        self.criterion = self._setup_criterion()
        
        # Initialize logging
        # self.writer = SummaryWriter(os.path.join(save_dir, 'tensorboard'))  # TensorBoardを無効化
        self.writer = None  # TensorBoardを無効化
        self._setup_wandb()
        
        # Training state
        self.current_epoch = 0
        self.best_dice = 0.0
        self.train_losses = []
        self.val_losses = []
        self.val_metrics = []
        
    def _setup_optimizer(self) -> optim.Optimizer:
        """Setup optimizer"""
        optimizer_name = self.config.get('optimizer', 'adam').lower()
        lr = self.config.get('learning_rate', 0.001)
        weight_decay = self.config.get('weight_decay', 1e-4)
        
        if optimizer_name == 'adam':
            return optim.Adam(self.model.parameters(), lr=lr, weight_decay=weight_decay)
        elif optimizer_name == 'sgd':
            momentum = self.config.get('momentum', 0.9)
            return optim.SGD(self.model.parameters(), lr=lr, momentum=momentum, weight_decay=weight_decay)
        else:
            raise ValueError(f"Unsupported optimizer: {optimizer_name}")
    
    def _setup_scheduler(self) -> Optional[optim.lr_scheduler._LRScheduler]:
        """Setup learning rate scheduler"""
        scheduler_name = self.config.get('scheduler', 'cosine').lower()
        
        if scheduler_name == 'cosine':
            return optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer, 
                T_max=self.config.get('epochs', 100)
            )
        elif scheduler_name == 'step':
            return optim.lr_scheduler.StepLR(
                self.optimizer,
                step_size=self.config.get('step_size', 30),
                gamma=self.config.get('gamma', 0.1)
            )
        elif scheduler_name == 'plateau':
            return optim.lr_scheduler.ReduceLROnPlateau(
                self.optimizer,
                mode='max',
                factor=0.5,
                patience=10,
                verbose=True
            )
        else:
            return None
    
    def _setup_criterion(self) -> nn.Module:
        """Setup loss function"""
        loss_name = self.config.get('loss', 'bce').lower()
        
        if loss_name == 'bce':
            return nn.BCEWithLogitsLoss()
        elif loss_name == 'dice':
            return DiceLoss()
        elif loss_name == 'focal':
            return FocalLoss()
        elif loss_name == 'combined':
            return CombinedLoss()
        else:
            raise ValueError(f"Unsupported loss function: {loss_name}")
    
    def _setup_wandb(self):
        """Setup Weights & Biases logging"""
        if self.config.get('use_wandb', False):
            wandb.init(
                project="mediseg-ai",
                config=self.config,
                name=f"experiment_{int(time.time())}"
            )
            wandb.watch(self.model)
    
    def train_epoch(self) -> Dict[str, float]:
        """Train for one epoch"""
        self.model.train()
        metrics = SegmentationMetrics()
        total_loss = 0.0
        
        pbar = tqdm(self.train_loader, desc=f"Epoch {self.current_epoch}")
        
        for batch_idx, (images, masks) in enumerate(pbar):
            images = images.to(self.device)
            masks = masks.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(images)
            
            # Calculate loss
            loss = self.criterion(outputs, masks.float())
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            # Update metrics
            total_loss += loss.item()
            metrics.update(outputs, masks)
            
            # Update progress bar
            pbar.set_postfix({
                'Loss': f'{loss.item():.4f}',
                'Dice': f'{metrics.compute()["dice"]:.4f}'
            })
            
            # Log to wandb
            if self.config.get('use_wandb', False):
                wandb.log({
                    'train/loss': loss.item(),
                    'train/learning_rate': self.optimizer.param_groups[0]['lr']
                })
        
        # Calculate epoch metrics
        epoch_loss = total_loss / len(self.train_loader)
        epoch_metrics = metrics.compute()
        
        return {
            'loss': epoch_loss,
            **epoch_metrics
        }
    
    def validate_epoch(self) -> Dict[str, float]:
        """Validate for one epoch"""
        self.model.eval()
        metrics = SegmentationMetrics()
        total_loss = 0.0
        
        with torch.no_grad():
            for images, masks in tqdm(self.val_loader, desc="Validation"):
                images = images.to(self.device)
                masks = masks.to(self.device)
                
                # Forward pass
                outputs = self.model(images)
                
                # Calculate loss
                loss = self.criterion(outputs, masks.float())
                total_loss += loss.item()
                
                # Update metrics
                metrics.update(outputs, masks)
        
        # Calculate epoch metrics
        epoch_loss = total_loss / len(self.val_loader)
        epoch_metrics = metrics.compute()
        
        return {
            'loss': epoch_loss,
            **epoch_metrics
        }
    
    def train(self, epochs: int) -> Dict[str, Any]:
        """Train the model for specified number of epochs"""
        print(f"Starting training for {epochs} epochs...")
        print(f"Device: {self.device}")
        print(f"Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")
        
        for epoch in range(epochs):
            self.current_epoch = epoch
            
            # Train
            train_metrics = self.train_epoch()
            self.train_losses.append(train_metrics['loss'])
            
            # Validate
            val_metrics = self.validate_epoch()
            self.val_losses.append(val_metrics['loss'])
            self.val_metrics.append(val_metrics)
            
            # Update scheduler
            if self.scheduler:
                if isinstance(self.scheduler, optim.lr_scheduler.ReduceLROnPlateau):
                    self.scheduler.step(val_metrics['dice'])
                else:
                    self.scheduler.step()
            
            # Log metrics
            self._log_metrics(epoch, train_metrics, val_metrics)
            
            # Save checkpoint
            if val_metrics['dice'] > self.best_dice:
                self.best_dice = val_metrics['dice']
                self._save_checkpoint(epoch, val_metrics, is_best=True)
            
            # Early stopping
            if self._check_early_stopping():
                print(f"Early stopping at epoch {epoch}")
                break
        
        print(f"Training completed! Best Dice: {self.best_dice:.4f}")
        return self._get_training_summary()
    
    def _log_metrics(self, epoch: int, train_metrics: Dict, val_metrics: Dict):
        """Log metrics to tensorboard and wandb"""
        # TensorBoard (無効化)
        # if self.writer:
        #     self.writer.add_scalar('Loss/Train', train_metrics['loss'], epoch)
        #     self.writer.add_scalar('Loss/Val', val_metrics['loss'], epoch)
        #     self.writer.add_scalar('Dice/Val', val_metrics['dice'], epoch)
        #     self.writer.add_scalar('IoU/Val', val_metrics['iou'], epoch)
        
        # Weights & Biases
        if self.config.get('use_wandb', False):
            wandb.log({
                'epoch': epoch,
                'train/loss': train_metrics['loss'],
                'val/loss': val_metrics['loss'],
                'val/dice': val_metrics['dice'],
                'val/iou': val_metrics['iou'],
                'val/accuracy': val_metrics['accuracy']
            })
    
    def _save_checkpoint(self, epoch: int, metrics: Dict, is_best: bool = False):
        """Save model checkpoint"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict() if self.scheduler else None,
            'metrics': metrics,
            'config': self.config
        }
        
        # Save regular checkpoint
        checkpoint_path = os.path.join(self.save_dir, f'checkpoint_epoch_{epoch}.pth')
        torch.save(checkpoint, checkpoint_path)
        
        # Save best model
        if is_best:
            best_path = os.path.join(self.save_dir, 'best_model.pth')
            torch.save(checkpoint, best_path)
            print(f"New best model saved with Dice: {metrics['dice']:.4f}")
    
    def _check_early_stopping(self) -> bool:
        """Check if early stopping criteria is met"""
        patience = self.config.get('early_stopping', {}).get('patience', 10)
        min_delta = self.config.get('early_stopping', {}).get('min_delta', 0.001)
        
        if len(self.val_metrics) < patience:
            return False
        
        recent_metrics = self.val_metrics[-patience:]
        best_recent = max(metric['dice'] for metric in recent_metrics)
        current_best = max(metric['dice'] for metric in self.val_metrics)
        
        return (current_best - best_recent) < min_delta
    
    def _get_training_summary(self) -> Dict[str, Any]:
        """Get training summary"""
        return {
            'best_dice': self.best_dice,
            'final_epoch': self.current_epoch,
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'val_metrics': self.val_metrics
        }


class DiceLoss(nn.Module):
    """Dice loss for segmentation"""
    
    def __init__(self, smooth: float = 1e-6):
        super().__init__()
        self.smooth = smooth
    
    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        pred = torch.sigmoid(pred)
        intersection = (pred * target).sum()
        dice = (2. * intersection + self.smooth) / (pred.sum() + target.sum() + self.smooth)
        return 1 - dice


class FocalLoss(nn.Module):
    """Focal loss for segmentation"""
    
    def __init__(self, alpha: float = 1.0, gamma: float = 2.0):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
    
    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        bce_loss = F.binary_cross_entropy_with_logits(pred, target, reduction='none')
        pt = torch.exp(-bce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * bce_loss
        return focal_loss.mean()


class CombinedLoss(nn.Module):
    """Combined BCE and Dice loss"""
    
    def __init__(self, bce_weight: float = 0.5, dice_weight: float = 0.5):
        super().__init__()
        self.bce_weight = bce_weight
        self.dice_weight = dice_weight
        self.bce = nn.BCEWithLogitsLoss()
        self.dice = DiceLoss()
    
    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        bce_loss = self.bce(pred, target)
        dice_loss = self.dice(pred, target)
        return self.bce_weight * bce_loss + self.dice_weight * dice_loss
