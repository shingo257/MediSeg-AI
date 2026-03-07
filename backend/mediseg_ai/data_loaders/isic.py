"""
ISIC (International Skin Imaging Collaboration) dataset loader for medical image segmentation
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
import pandas as pd


class ISICDataset(Dataset):
    """
    ISIC dataset for skin lesion segmentation
    
    Args:
        root_dir: Root directory containing ISIC dataset
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
        
        # Set up paths
        self.image_dir = os.path.join(root_dir, 'images')
        self.mask_dir = os.path.join(root_dir, 'masks')
        
        # Get list of image files
        self.image_files = self._get_image_files()
        
        print(f"Loaded {len(self.image_files)} {split} samples from ISIC dataset")
    
    def _get_image_files(self) -> List[str]:
        """Get list of image files for the specified split"""
        image_files = []
        
        if os.path.exists(self.image_dir):
            for filename in os.listdir(self.image_dir):
                if filename.endswith(('.jpg', '.jpeg', '.png')):
                    # Check if corresponding mask exists
                    mask_name = filename.replace('.jpg', '.png').replace('.jpeg', '.png')
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
        mask_name = filename.replace('.jpg', '.png').replace('.jpeg', '.png')
        mask_path = os.path.join(self.mask_dir, mask_name)
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        
        # Convert mask to binary (0 or 1)
        mask = (mask > 128).astype(np.uint8)
        
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


def get_isic_transforms(
    image_size: Tuple[int, int] = (256, 256),
    is_training: bool = True
) -> A.Compose:
    """
    Get augmentation transforms for ISIC dataset
    
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
            A.VerticalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
            A.RandomBrightnessContrast(
                brightness_limit=0.3,
                contrast_limit=0.3,
                p=0.5
            ),
            A.RandomGamma(gamma_limit=(80, 120), p=0.5),
            A.GaussNoise(var_limit=(10.0, 50.0), p=0.3),
            A.ElasticTransform(
                alpha=1,
                sigma=50,
                alpha_affine=50,
                p=0.3
            ),
            A.GridDistortion(
                num_steps=5,
                distort_limit=0.3,
                p=0.3
            ),
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


from mediseg_ai.data_loaders.registry import DatasetRegistry

@DatasetRegistry.register("isic")
def create_isic_dataloaders(
    root_dir: str,
    batch_size: int = 16,
    num_workers: int = 4,
    image_size: Tuple[int, int] = (256, 256),
    train_split: float = 0.8,
    val_split: float = 0.1
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Create train, validation, and test dataloaders for ISIC dataset
    
    Args:
        root_dir: Root directory of ISIC dataset
        batch_size: Batch size for dataloaders
        num_workers: Number of worker processes
        image_size: Target image size
        train_split: Fraction of data for training
        val_split: Fraction of data for validation
        
    Returns:
        Tuple of (train_loader, val_loader, test_loader)
    """
    # Get all image files
    image_dir = os.path.join(root_dir, 'images')
    all_files = []
    
    if os.path.exists(image_dir):
        for filename in os.listdir(image_dir):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                mask_name = filename.replace('.jpg', '.png').replace('.jpeg', '.png')
                mask_path = os.path.join(root_dir, 'masks', mask_name)
                if os.path.exists(mask_path):
                    all_files.append(filename)
    
    # Split data
    np.random.seed(42)
    np.random.shuffle(all_files)
    
    n_total = len(all_files)
    n_train = int(n_total * train_split)
    n_val = int(n_total * val_split)
    
    train_files = all_files[:n_train]
    val_files = all_files[n_train:n_train + n_val]
    test_files = all_files[n_train + n_val:]
    
    print(f"Data split: {len(train_files)} train, {len(val_files)} val, {len(test_files)} test")
    
    # Get transforms
    train_transform = get_isic_transforms(image_size, is_training=True)
    val_transform = get_isic_transforms(image_size, is_training=False)
    
    # Create datasets
    train_dataset = ISICDataset(
        root_dir=root_dir,
        split='train',
        transform=train_transform
    )
    
    val_dataset = ISICDataset(
        root_dir=root_dir,
        split='val',
        transform=val_transform
    )
    
    test_dataset = ISICDataset(
        root_dir=root_dir,
        split='test',
        transform=val_transform
    )
    
    # Override file lists for proper splitting
    train_dataset.image_files = train_files
    val_dataset.image_files = val_files
    test_dataset.image_files = test_files
    
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
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
        drop_last=False
    )
    
    return train_loader, val_loader, test_loader


def test_isic_dataset():
    """Test function for ISIC dataset"""
    print("ISIC Dataset Test")
    print("Note: This test requires the actual ISIC dataset to be downloaded")
    print("Dataset structure should be:")
    print("ISIC/")
    print("├── images/")
    print("├── masks/")
    print("└── ...")


if __name__ == "__main__":
    test_isic_dataset()
