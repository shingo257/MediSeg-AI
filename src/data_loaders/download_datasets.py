"""
MediSeg.AI - 無料データセット自動ダウンロード機能
医療画像と一般画像の無料データセットを自動でダウンロード・読み込み
"""

import os
import sys
import requests
import zipfile
import tarfile
import shutil
import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns

# プロジェクトのパスを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class DatasetDownloader:
    """無料データセットの自動ダウンロード・管理クラス"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # データセット情報
        self.datasets = {
            # 医療画像データセット
            "isic_sample": {
                "name": "ISIC Sample Dataset",
                "description": "皮膚病変セグメンテーション用サンプルデータ",
                "url": "https://isic-challenge-data.s3.amazonaws.com/2018/ISIC2018_Task1-2_Training_Input.zip",
                "type": "medical",
                "format": "zip",
                "extract_to": "isic_sample",
                "images_dir": "ISIC2018_Task1-2_Training_Input",
                "masks_dir": "ISIC2018_Task1-2_Training_GroundTruth"
            },
            
            # 一般画像データセット
            "pascal_voc_sample": {
                "name": "Pascal VOC Sample Dataset",
                "description": "オブジェクトセグメンテーション用サンプルデータ",
                "url": "https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz",
                "type": "general",
                "format": "tar.gz",
                "extract_to": "pascal_voc_sample",
                "images_dir": "cifar-10-batches-py",
                "masks_dir": None
            },
            
            # 合成データセット（デモ用）
            "synthetic_medical": {
                "name": "Synthetic Medical Dataset",
                "description": "合成医療画像データセット（デモ用）",
                "url": None,  # ローカル生成
                "type": "medical",
                "format": "synthetic",
                "extract_to": "synthetic_medical",
                "images_dir": "images",
                "masks_dir": "masks"
            }
        }
    
    def download_file(self, url, filepath, chunk_size=8192):
        """ファイルをダウンロード"""
        try:
            print(f"📥 Downloading {url}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r📊 Progress: {progress:.1f}%", end="", flush=True)
            
            print(f"\n✅ Download completed: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False
    
    def extract_archive(self, archive_path, extract_to):
        """アーカイブを展開"""
        try:
            print(f"📦 Extracting {archive_path}...")
            
            if archive_path.suffix == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
            elif archive_path.suffix == '.gz' or '.tar' in archive_path.name:
                with tarfile.open(archive_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(extract_to)
            else:
                print(f"❌ Unsupported archive format: {archive_path.suffix}")
                return False
            
            print(f"✅ Extraction completed: {extract_to}")
            return True
            
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return False
    
    def generate_synthetic_medical_data(self, output_dir, num_samples=50):
        """合成医療画像データを生成"""
        try:
            print(f"🎨 Generating synthetic medical dataset...")
            
            images_dir = output_dir / "images"
            masks_dir = output_dir / "masks"
            images_dir.mkdir(parents=True, exist_ok=True)
            masks_dir.mkdir(parents=True, exist_ok=True)
            
            for i in range(num_samples):
                # 合成画像の生成
                img = self._generate_synthetic_image()
                mask = self._generate_synthetic_mask(img.shape)
                
                # 画像とマスクを保存
                img_path = images_dir / f"sample_{i:03d}.png"
                mask_path = masks_dir / f"sample_{i:03d}.png"
                
                cv2.imwrite(str(img_path), img)
                cv2.imwrite(str(mask_path), mask)
                
                if (i + 1) % 10 == 0:
                    print(f"📊 Generated {i + 1}/{num_samples} samples")
            
            print(f"✅ Synthetic dataset generated: {output_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Synthetic data generation failed: {e}")
            return False
    
    def _generate_synthetic_image(self, size=(256, 256)):
        """合成画像を生成"""
        # ベース画像（ノイズ付き）
        img = np.random.randint(0, 255, (*size, 3), dtype=np.uint8)
        
        # 医療画像らしい特徴を追加
        # 1. 背景のグラデーション
        y, x = np.ogrid[:size[0], :size[1]]
        center_x, center_y = size[1] // 2, size[0] // 2
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        gradient = 1 - (distance / np.sqrt(center_x**2 + center_y**2))
        gradient = np.clip(gradient, 0, 1)
        
        for c in range(3):
            img[:, :, c] = img[:, :, c] * gradient + 50 * (1 - gradient)
        
        # 2. テクスチャの追加
        noise = np.random.normal(0, 20, img.shape).astype(np.uint8)
        img = np.clip(img + noise, 0, 255)
        
        # 3. 医療画像らしい色調整
        img = cv2.GaussianBlur(img, (3, 3), 0)
        
        return img
    
    def _generate_synthetic_mask(self, img_shape):
        """合成マスクを生成"""
        mask = np.zeros(img_shape[:2], dtype=np.uint8)
        
        # 複数の楕円形領域を生成
        num_regions = np.random.randint(1, 4)
        
        for _ in range(num_regions):
            # 楕円のパラメータ
            center = (
                np.random.randint(50, img_shape[1] - 50),
                np.random.randint(50, img_shape[0] - 50)
            )
            axes = (
                np.random.randint(20, 60),
                np.random.randint(20, 60)
            )
            angle = np.random.randint(0, 180)
            
            # 楕円を描画
            cv2.ellipse(mask, center, axes, angle, 0, 360, 255, -1)
        
        # 境界をぼかす
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        
        return mask
    
    def download_dataset(self, dataset_name):
        """指定されたデータセットをダウンロード"""
        if dataset_name not in self.datasets:
            print(f"❌ Unknown dataset: {dataset_name}")
            return False
        
        dataset_info = self.datasets[dataset_name]
        dataset_dir = self.data_dir / dataset_info["extract_to"]
        
        print(f"🚀 Downloading {dataset_info['name']}...")
        print(f"📝 Description: {dataset_info['description']}")
        
        # 既に存在する場合はスキップ
        if dataset_dir.exists():
            print(f"✅ Dataset already exists: {dataset_dir}")
            return True
        
        # 合成データセットの場合
        if dataset_info["format"] == "synthetic":
            return self.generate_synthetic_medical_data(dataset_dir)
        
        # 通常のダウンロード
        if not dataset_info["url"]:
            print(f"❌ No download URL for dataset: {dataset_name}")
            return False
        
        # ダウンロード
        archive_path = self.data_dir / f"{dataset_name}.{dataset_info['format']}"
        if not self.download_file(dataset_info["url"], archive_path):
            return False
        
        # 展開
        if not self.extract_archive(archive_path, dataset_dir):
            return False
        
        # アーカイブファイルを削除
        archive_path.unlink()
        
        print(f"✅ Dataset downloaded successfully: {dataset_dir}")
        return True
    
    def list_available_datasets(self):
        """利用可能なデータセット一覧を表示"""
        print("📚 Available Datasets:")
        print("=" * 50)
        
        for key, info in self.datasets.items():
            status = "✅ Available" if (self.data_dir / info["extract_to"]).exists() else "❌ Not downloaded"
            print(f"🔹 {key}")
            print(f"   Name: {info['name']}")
            print(f"   Type: {info['type']}")
            print(f"   Status: {status}")
            print(f"   Description: {info['description']}")
            print()
    
    def get_dataset_path(self, dataset_name):
        """データセットのパスを取得"""
        if dataset_name not in self.datasets:
            return None
        
        dataset_info = self.datasets[dataset_name]
        dataset_dir = self.data_dir / dataset_info["extract_to"]
        
        if not dataset_dir.exists():
            return None
        
        return dataset_dir
    
    def create_sample_loader(self, dataset_name, batch_size=4):
        """サンプルデータローダーを作成"""
        dataset_path = self.get_dataset_path(dataset_name)
        if not dataset_path:
            print(f"❌ Dataset not found: {dataset_name}")
            return None
        
        dataset_info = self.datasets[dataset_name]
        
        if dataset_info["type"] == "medical":
            return self._create_medical_loader(dataset_path, dataset_info, batch_size)
        else:
            return self._create_general_loader(dataset_path, dataset_info, batch_size)
    
    def _create_medical_loader(self, dataset_path, dataset_info, batch_size):
        """医療画像データローダーを作成"""
        images_dir = dataset_path / dataset_info["images_dir"]
        masks_dir = dataset_path / dataset_info["masks_dir"]
        
        if not images_dir.exists():
            print(f"❌ Images directory not found: {images_dir}")
            return None
        
        # 画像ファイルのリストを取得
        image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
        
        if not image_files:
            print(f"❌ No image files found in: {images_dir}")
            return None
        
        print(f"📊 Found {len(image_files)} images")
        
        # サンプル画像を表示
        self._display_sample_images(image_files[:4], masks_dir)
        
        return image_files
    
    def _create_general_loader(self, dataset_path, dataset_info, batch_size):
        """一般画像データローダーを作成"""
        images_dir = dataset_path / dataset_info["images_dir"]
        
        if not images_dir.exists():
            print(f"❌ Images directory not found: {images_dir}")
            return None
        
        # 画像ファイルのリストを取得
        image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
        
        if not image_files:
            print(f"❌ No image files found in: {images_dir}")
            return None
        
        print(f"📊 Found {len(image_files)} images")
        
        # サンプル画像を表示
        self._display_sample_images(image_files[:4])
        
        return image_files
    
    def _display_sample_images(self, image_files, masks_dir=None):
        """サンプル画像を表示"""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(12, 8))
            fig.suptitle("Sample Images from Dataset", fontsize=16, fontweight='bold')
            
            for i, img_path in enumerate(image_files[:4]):
                row, col = i // 2, i % 2
                
                # 画像を読み込み
                img = cv2.imread(str(img_path))
                if img is not None:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    axes[row, col].imshow(img)
                    axes[row, col].set_title(f"Sample {i+1}", fontsize=12)
                    axes[row, col].axis('off')
                    
                    # マスクがある場合は表示
                    if masks_dir and masks_dir.exists():
                        mask_path = masks_dir / img_path.name
                        if mask_path.exists():
                            mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
                            if mask is not None:
                                # マスクをオーバーレイ
                                overlay = img.copy()
                                overlay[mask > 0] = [255, 0, 0]  # 赤色でオーバーレイ
                                axes[row, col].imshow(overlay, alpha=0.5)
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print(f"❌ Failed to display sample images: {e}")

def main():
    """メイン関数"""
    print("🏥 MediSeg.AI - Free Dataset Downloader")
    print("=" * 50)
    
    downloader = DatasetDownloader()
    
    # 利用可能なデータセット一覧を表示
    downloader.list_available_datasets()
    
    # 合成医療データセットを生成（デモ用）
    print("🎨 Generating synthetic medical dataset for demo...")
    if downloader.download_dataset("synthetic_medical"):
        print("✅ Synthetic dataset ready!")
        
        # サンプルローダーを作成
        sample_loader = downloader.create_sample_loader("synthetic_medical")
        if sample_loader:
            print(f"📊 Sample loader created with {len(sample_loader)} images")
    
    print("\n🎉 Dataset downloader ready!")
    print("Use this in your training scripts to automatically download datasets.")

if __name__ == "__main__":
    main()
