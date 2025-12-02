"""
Pascal VOC 2012 dataset loader for semantic segmentation
"""

import os
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import numpy as np
import cv2
from typing import Tuple, List, Optional, Callable
import albumentations as A
from albumentations.pytorch import ToTensorV2


class PascalVOCDataset(Dataset):
    """
    Pascal VOC 2012 dataset for semantic segmentation
    
    Args:
        root_dir: Root directory containing VOC2012 dataset
        split: Dataset split ('train', 'val', 'test')
        transform: Optional transform to be applied on images
        target_transform: Optional transform to be applied on masks
    """
    
    def __init__(
        self,
        root_dir: str,
        split: str = 'train',
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None
    ):
        self.root_dir = root_dir
        self.split = split
        self.transform = transform
        self.target_transform = target_transform
        
        # VOC2012 class names (21 classes including background)
        self.class_names = [
            'background', 'aeroplane', 'bicycle', 'bird', 'boat', 'bottle',
            'bus', 'car', 'cat', 'chair', 'cow', 'diningtable', 'dog',
            'horse', 'motorbike', 'person', 'pottedplant', 'sheep', 'sofa',
            'train', 'tvmonitor'
        ]
        
        self.num_classes = len(self.class_names)
        
        # Set up paths
        self.image_dir = os.path.join(root_dir, 'JPEGImages')
        self.mask_dir = os.path.join(root_dir, 'SegmentationClass')
        
        # Get list of image files
        self.image_files = self._get_image_files()
        
        print(f"Loaded {len(self.image_files)} {split} samples")
    
    def _get_image_files(self) -> List[str]:
        """Get list of image files for the specified split"""
        # For simplicity, we'll use all images in the directory
        # In practice, you would use the train/val split files
        image_files = []
        
        if os.path.exists(self.image_dir):
            for filename in os.listdir(self.image_dir):
                if filename.endswith('.jpg'):
                    # Check if corresponding mask exists
                    mask_name = filename.replace('.jpg', '.png')
                    mask_path = os.path.join(self.mask_dir, mask_name)
                    if os.path.exists(mask_path):
                        image_files.append(filename)
        
        return image_files
    
    def __len__(self) -> int:
        return len(self.image_files)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get item by index"""
        filename = self.image_files[idx]
        
        # Load image
        image_path = os.path.join(self.image_dir, filename)
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Load mask
        mask_name = filename.replace('.jpg', '.png')
        mask_path = os.path.join(self.mask_dir, mask_name)
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        
        # Apply transforms
        if self.transform:
            transformed = self.transform(image=image, mask=mask)
            image = transformed['image']
            mask = transformed['mask']
        else:
            # Convert to tensors
            image = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0
            mask = torch.from_numpy(mask).long()
        
        return image, mask


def get_pascal_voc_transforms(
    image_size: Tuple[int, int] = (256, 256),
    is_training: bool = True
) -> A.Compose:
    """
    Get augmentation transforms for Pascal VOC dataset
    
    Args:
        image_size: Target image size (height, width)
        is_training: Whether to apply training augmentations
        
    Returns:
        Albumentations compose transform
    """
    if is_training:
        transform = A.Compose([
            A.Resize(image_size[0], image_size[1]),
            A.HorizontalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
            A.RandomBrightnessContrast(
                brightness_limit=0.2,
                contrast_limit=0.2,
                p=0.5
            ),
            A.RandomGamma(gamma_limit=(80, 120), p=0.5),
            A.GaussNoise(var_limit=(10.0, 50.0), p=0.3),
            A.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
            ToTensorV2()
        ])
    else:
        transform = A.Compose([
            A.Resize(image_size[0], image_size[1]),
            A.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
            ToTensorV2()
        ])
    
    return transform


def create_pascal_voc_dataloaders(
    root_dir: str,
    batch_size: int = 16,
    num_workers: int = 4,
    image_size: Tuple[int, int] = (256, 256)
) -> Tuple[DataLoader, DataLoader]:
    """
    Create train and validation dataloaders for Pascal VOC
    
    Args:
        root_dir: Root directory of VOC2012 dataset
        batch_size: Batch size for dataloaders
        num_workers: Number of worker processes
        image_size: Target image size
        
    Returns:
        Tuple of (train_loader, val_loader)
    """
    # Get transforms
    train_transform = get_pascal_voc_transforms(image_size, is_training=True)
    val_transform = get_pascal_voc_transforms(image_size, is_training=False)
    
    # Create datasets
    train_dataset = PascalVOCDataset(
        root_dir=root_dir,
        split='train',
        transform=train_transform
    )
    
    val_dataset = PascalVOCDataset(
        root_dir=root_dir,
        split='val',
        transform=val_transform
    )
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
        drop_last=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
        drop_last=False
    )
    
    return train_loader, val_loader


def test_pascal_voc_dataset():
    """Test function for Pascal VOC dataset"""
    # This is a placeholder test - in practice you would need the actual dataset
    print("Pascal VOC Dataset Test")
    print("Note: This test requires the actual VOC2012 dataset to be downloaded")
    print("Dataset structure should be:")
    print("VOC2012/")
    print("├── JPEGImages/")
    print("├── SegmentationClass/")
    print("└── ...")


if __name__ == "__main__":
    test_pascal_voc_dataset()
