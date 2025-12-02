"""
MediSeg.AI - 自動データセット読み込み機能
無料データセットを自動でダウンロード・読み込み・前処理
"""

import os
import sys
import torch
import numpy as np
import cv2
from pathlib import Path
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import albumentations as A
from albumentations.pytorch import ToTensorV2

# プロジェクトのパスを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from data_loaders.download_datasets import DatasetDownloader

class AutoDataset(Dataset):
    """自動データセット読み込みクラス"""
    
    def __init__(self, dataset_name, data_dir="data", transform=None, target_transform=None, download=True):
        self.dataset_name = dataset_name
        self.data_dir = Path(data_dir)
        self.transform = transform
        self.target_transform = target_transform
        
        # データセットダウンローダー
        self.downloader = DatasetDownloader(data_dir)
        
        # データセットをダウンロード（必要に応じて）
        if download:
            self.downloader.download_dataset(dataset_name)
        
        # データセット情報を取得
        self.dataset_info = self.downloader.datasets[dataset_name]
        self.dataset_path = self.downloader.get_dataset_path(dataset_name)
        
        if not self.dataset_path:
            raise ValueError(f"Dataset not found: {dataset_name}")
        
        # 画像とマスクのパスを取得
        self.image_paths, self.mask_paths = self._load_paths()
        
        print(f"📊 Loaded {len(self.image_paths)} samples from {dataset_name}")
    
    def _load_paths(self):
        """画像とマスクのパスを取得"""
        images_dir = self.dataset_path / self.dataset_info["images_dir"]
        masks_dir = self.dataset_path / self.dataset_info["masks_dir"] if self.dataset_info["masks_dir"] else None
        
        if not images_dir.exists():
            raise ValueError(f"Images directory not found: {images_dir}")
        
        # 画像ファイルを取得
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        image_files = []
        for ext in image_extensions:
            image_files.extend(images_dir.glob(f"*{ext}"))
            image_files.extend(images_dir.glob(f"*{ext.upper()}"))
        
        image_files = sorted(image_files)
        
        if not image_files:
            raise ValueError(f"No image files found in: {images_dir}")
        
        # マスクファイルを取得（存在する場合）
        mask_files = []
        if masks_dir and masks_dir.exists():
            for img_path in image_files:
                mask_path = masks_dir / img_path.name
                if mask_path.exists():
                    mask_files.append(mask_path)
                else:
                    mask_files.append(None)
        else:
            mask_files = [None] * len(image_files)
        
        return image_files, mask_files
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        # 画像を読み込み
        img_path = self.image_paths[idx]
        image = cv2.imread(str(img_path))
        if image is None:
            raise ValueError(f"Failed to load image: {img_path}")
        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # マスクを読み込み（存在する場合）
        mask = None
        if self.mask_paths[idx] is not None:
            mask = cv2.imread(str(self.mask_paths[idx]), cv2.IMREAD_GRAYSCALE)
            if mask is None:
                print(f"Warning: Failed to load mask: {self.mask_paths[idx]}")
                mask = np.zeros(image.shape[:2], dtype=np.uint8)
        else:
            # マスクがない場合は空のマスクを生成（警告を表示）
            mask = np.zeros(image.shape[:2], dtype=np.uint8)
            print(f"Warning: No mask found for image {self.image_paths[idx]}, using empty mask")
        
        # 変換を適用
        if self.transform:
            if isinstance(self.transform, A.Compose):
                # Albumentationsの場合
                transformed = self.transform(image=image, mask=mask)
                image = transformed['image']
                mask = transformed['mask']
            else:
                # その他の変換
                image = self.transform(image)
                if self.target_transform:
                    mask = self.target_transform(mask)
        
        # テンソルに変換
        if not isinstance(image, torch.Tensor):
            image = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0
        
        if not isinstance(mask, torch.Tensor):
            mask = torch.from_numpy(mask).float() / 255.0
        
        return image, mask
    
    def get_sample(self, idx=0):
        """サンプルを取得（変換なし）"""
        img_path = self.image_paths[idx]
        image = cv2.imread(str(img_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        mask = None
        if self.mask_paths[idx] is not None:
            mask = cv2.imread(str(self.mask_paths[idx]), cv2.IMREAD_GRAYSCALE)
        
        return image, mask, img_path.name

def create_auto_dataloaders(dataset_name, data_dir="data", batch_size=4, num_workers=2, download=True):
    """自動データローダーを作成"""
    
    # 医療画像用の変換
    if "medical" in dataset_name or "isic" in dataset_name:
        transform = A.Compose([
            A.Resize(256, 256),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
            A.ElasticTransform(p=0.3, alpha=1, sigma=50, alpha_affine=50),
            A.GaussNoise(p=0.2),
            A.GaussianBlur(p=0.2),
            A.RandomBrightnessContrast(p=0.3),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ])
    else:
        # 一般画像用の変換
        transform = A.Compose([
            A.Resize(256, 256),
            A.HorizontalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
            A.RandomBrightnessContrast(p=0.3),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ])
    
    # データセットを作成
    dataset = AutoDataset(
        dataset_name=dataset_name,
        data_dir=data_dir,
        transform=transform,
        download=download
    )
    
    # データローダーを作成
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True
    )
    
    return dataloader, dataset

def demo_auto_dataset():
    """自動データセットのデモ"""
    print("🚀 MediSeg.AI - Auto Dataset Demo")
    print("=" * 50)
    
    # 合成医療データセットを試す
    try:
        print("📊 Loading synthetic medical dataset...")
        dataloader, dataset = create_auto_dataloaders(
            dataset_name="synthetic_medical",
            batch_size=4,
            num_workers=0  # Windowsでは0に設定
        )
        
        print(f"✅ Dataset loaded successfully!")
        print(f"📊 Total samples: {len(dataset)}")
        print(f"📊 Batch size: {dataloader.batch_size}")
        
        # サンプルを表示
        print("\n🎨 Sample images:")
        for i in range(min(4, len(dataset))):
            image, mask, name = dataset.get_sample(i)
            print(f"📸 Sample {i+1}: {name}")
            print(f"   Image shape: {image.shape}")
            print(f"   Mask shape: {mask.shape if mask is not None else 'None'}")
        
        # バッチを取得
        print("\n🔄 Loading batch...")
        for batch_idx, (images, masks) in enumerate(dataloader):
            print(f"📦 Batch {batch_idx + 1}:")
            print(f"   Images shape: {images.shape}")
            print(f"   Masks shape: {masks.shape}")
            print(f"   Image range: [{images.min():.3f}, {images.max():.3f}]")
            print(f"   Mask range: [{masks.min():.3f}, {masks.max():.3f}]")
            
            if batch_idx >= 2:  # 最初の3バッチのみ表示
                break
        
        print("\n✅ Auto dataset demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_auto_dataset()
