# 📚 MediSeg.AI - 無料データセットガイド

## 🎯 概要

MediSeg.AIでは、手元にデータがない場合でも、無料のデータセットを自動でダウンロード・読み込みできる機能を提供しています。

## 🚀 使用方法

### 1. 自動データセット（合成データ）
```bash
# 合成医療画像データセットを生成・読み込み
python main.py --mode auto_dataset
```

### 2. 実世界データセット
```bash
# 実世界データセットの一覧表示・ダウンロード
python main.py --mode real_datasets
```

## 📊 利用可能なデータセット

### 🏥 医療画像データセット

#### 1. ISIC 2018 Challenge Dataset
- **説明**: 皮膚病変セグメンテーション用実データ
- **サイズ**: ~2GB
- **URL**: 自動ダウンロード
- **特徴**: 実際の皮膚病変画像とアノテーション

#### 2. ISIC 2019 Challenge Dataset
- **説明**: 皮膚病変セグメンテーション用実データ（2019年版）
- **サイズ**: ~3GB
- **URL**: 自動ダウンロード
- **特徴**: より多様な皮膚病変データ

#### 3. Small Medical Dataset（生成）
- **説明**: 小規模医療画像データセット（デモ用）
- **サイズ**: ~50MB
- **特徴**: 現実的な医療画像を合成生成
- **用途**: デモ・テスト用

### 🖼️ 一般画像データセット

#### 1. Pascal VOC 2012 Dataset
- **説明**: オブジェクトセグメンテーション用実データ
- **サイズ**: ~2GB
- **URL**: 自動ダウンロード
- **特徴**: 20クラスのオブジェクトセグメンテーション

#### 2. COCO Sample Dataset
- **説明**: COCOデータセットのサンプル（小規模）
- **サイズ**: ~100MB
- **URL**: 自動ダウンロード
- **特徴**: 多様なオブジェクトクラス

## 🛠️ 技術的特徴

### 自動ダウンロード機能
- **進捗表示**: ダウンロード進捗のリアルタイム表示
- **エラーハンドリング**: ネットワークエラーの自動処理
- **重複回避**: 既存データセットの重複ダウンロード防止

### データ前処理
- **医療画像用**: エラスティック変形、ガンマ補正、ノイズ除去
- **一般画像用**: 標準的なデータ拡張
- **自動正規化**: ImageNet統計による正規化

### データローダー
- **バッチ処理**: 効率的なバッチ読み込み
- **マルチプロセシング**: 並列データ読み込み
- **メモリ最適化**: 大容量データセット対応

## 📝 使用例

### 基本的な使用方法
```python
from src.data_loaders.auto_dataset import create_auto_dataloaders

# 合成医療データセットを読み込み
dataloader, dataset = create_auto_dataloaders(
    dataset_name="synthetic_medical",
    batch_size=4,
    num_workers=2
)

# データをイテレート
for batch_idx, (images, masks) in enumerate(dataloader):
    print(f"Batch {batch_idx}: {images.shape}, {masks.shape}")
```

### 実世界データセットの使用
```python
from src.data_loaders.real_datasets import RealDatasetDownloader

# ダウンローダーを作成
downloader = RealDatasetDownloader()

# ISIC 2018データセットをダウンロード
downloader.download_dataset("isic_2018")

# データセットパスを取得
dataset_path = downloader.get_dataset_path("isic_2018")
```

## 🎨 合成データセットの特徴

### 医療画像生成
- **現実的な色調**: 医療画像らしいグレースケール風
- **組織構造**: 血管や臓器の構造を模擬
- **ノイズパターン**: 実際の医療画像に近いノイズ
- **病変領域**: 不規則な形状の病変マスク

### データ拡張
- **エラスティック変形**: 医療画像に適した変形
- **ガンマ補正**: コントラスト調整
- **ノイズ除去**: 医療画像品質向上
- **回転・反転**: 標準的なデータ拡張

## 🔧 カスタマイズ

### 新しいデータセットの追加
```python
# データセット情報を追加
new_dataset = {
    "name": "Custom Dataset",
    "description": "カスタムデータセット",
    "url": "https://example.com/dataset.zip",
    "type": "medical",
    "format": "zip",
    "extract_to": "custom_dataset",
    "images_dir": "images",
    "masks_dir": "masks",
    "size": "~500MB"
}

# ダウンローダーに追加
downloader.datasets["custom"] = new_dataset
```

### データ変換のカスタマイズ
```python
# カスタム変換を作成
custom_transform = A.Compose([
    A.Resize(512, 512),
    A.RandomRotate90(p=0.5),
    A.ElasticTransform(p=0.3),
    A.GaussNoise(p=0.2),
    A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ToTensorV2()
])

# データローダーに適用
dataloader, dataset = create_auto_dataloaders(
    dataset_name="synthetic_medical",
    transform=custom_transform
)
```

## 📊 パフォーマンス

### ダウンロード速度
- **小規模データセット**: 数分で完了
- **大規模データセット**: ネットワーク速度に依存
- **並列ダウンロード**: 複数ファイルの同時処理

### メモリ使用量
- **合成データセット**: 低メモリ使用量
- **実世界データセット**: データサイズに依存
- **バッチ処理**: メモリ効率的な読み込み

## 🚨 注意事項

### ネットワーク要件
- **安定したインターネット接続**: 大容量データセットのダウンロード
- **十分なディスク容量**: データセットサイズに応じた容量確保
- **ファイアウォール**: 外部URLへのアクセス許可

### ライセンス
- **ISICデータセット**: 研究用途での使用
- **Pascal VOC**: 学術研究用途
- **COCO**: 商用利用可能

## 🎉 まとめ

MediSeg.AIの無料データセット機能により、手元にデータがない場合でも：

1. **即座に開始**: 合成データでデモ実行
2. **実データ学習**: 実世界データセットで本格学習
3. **カスタマイズ**: 独自データセットの追加
4. **効率的処理**: 自動前処理とデータローダー

**データ不足の心配なく、MediSeg.AIで医療画像セグメンテーションを始められます！** 🚀
