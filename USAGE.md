# MediSeg.AI 使用方法ガイド

## 🚀 クイックスタート

### 1. 環境セットアップ

```bash
# 仮想環境の作成とアクティブ化
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 依存関係のインストール
pip install -r requirements.txt
```

### 2. デモ実行

```bash
# 基本的なデモを実行
python main.py --mode demo
```

### 3. Web GUIの起動

```bash
# Web GUI起動スクリプトを使用（推奨）
python web_gui_launcher.py

# または、main.pyから起動
python main.py --mode gui

# または、直接web_gui.pyを実行（デバッグモード）
python -m src.gui.web_gui
```

#### 環境変数による設定

```bash
# ポート番号を変更
export MEDISEG_PORT=5000

# ホストを変更
export MEDISEG_HOST=0.0.0.0

# デバッグモードを有効化
export MEDISEG_DEBUG=true

# ブラウザの自動起動を無効化
export MEDISEG_AUTO_OPEN_BROWSER=false

# ブラウザ起動の遅延時間を変更（秒）
export MEDISEG_BROWSER_DELAY=5.0
```

起動後、ブラウザで `http://localhost:8080` にアクセスしてください。

## 📊 データセットの準備

### Pascal VOC 2012 データセット

```bash
# データセットのダウンロード（手動）
# 1. http://host.robots.ox.ac.uk/pascal/VOC/voc2012/ からダウンロード
# 2. 以下の構造で配置:
# data/pascal_voc/
# ├── JPEGImages/
# ├── SegmentationClass/
# └── ...
```

### ISIC 医療データセット

```bash
# ISICデータセットのダウンロード（手動）
# 1. https://challenge.isic-archive.com/ からダウンロード
# 2. 以下の構造で配置:
# data/medical/isic/
# ├── images/
# ├── masks/
# └── ...
```

## 🏋️ モデル訓練

### 1. Pascal VOC での訓練

```bash
# U-Netモデルの訓練
python main.py --mode train --data_dir data/pascal_voc --save_dir results/pascal_voc
```

### 2. 医療画像での訓練

```bash
# ISICデータセットでの訓練
python main.py --mode train_medical --data_dir data/medical/isic --save_dir results/isic
```

### 3. カスタム設定での訓練

```bash
# カスタム設定ファイルを使用
python main.py --mode train --config configs/custom_config.yaml --data_dir data/pascal_voc
```

## 📈 モデル評価

### 1. 訓練済みモデルの評価

```bash
# モデルの評価
python main.py --mode eval --model_path results/best_model.pth --data_dir data/pascal_voc
```

### 2. 可視化付き評価

```bash
# 可視化付きで評価
python src/evaluation/evaluate.py --model_path results/best_model.pth --data_dir data/pascal_voc --visualize
```

## 🔍 モデル比較

### 1. U-Net vs DeepLabV3+ の比較

```bash
# Pascal VOC での比較
python main.py --mode compare --dataset pascal_voc --data_dir data/pascal_voc

# ISIC での比較
python main.py --mode compare --dataset isic --data_dir data/medical/isic
```

## 📝 設定ファイル

### 基本設定 (configs/base_config.yaml)

```yaml
# データ設定
data:
  batch_size: 16
  num_workers: 4
  image_size: [256, 256]

# モデル設定
model:
  name: "unet"
  num_classes: 1
  in_channels: 3

# 訓練設定
training:
  epochs: 100
  learning_rate: 0.001
  optimizer: "adam"
  scheduler: "cosine"
```

### 医療画像設定 (configs/isic_config.yaml)

```yaml
# 医療画像用の設定
medical:
  dataset: "isic"
  lesion_type: "melanoma"
  elastic_transform: true
  grid_distortion: true
```

## 🛠️ 開発者向け

### 1. 新しいモデルの追加

```python
# src/models/new_model.py
class NewModel(nn.Module):
    def __init__(self, ...):
        # モデル定義
        pass
    
    def forward(self, x):
        # フォワードパス
        pass
```

### 2. 新しいデータセットの追加

```python
# src/data_loaders/new_dataset.py
class NewDataset(Dataset):
    def __init__(self, ...):
        # データセット定義
        pass
    
    def __getitem__(self, idx):
        # データ取得
        pass
```

### 3. カスタム評価指標の追加

```python
# src/evaluation/custom_metrics.py
def custom_metric(pred, target):
    # カスタム指標の実装
    pass
```

## 📊 実験管理

### 1. Weights & Biases の使用

```python
# 設定ファイルで有効化
logging:
  use_wandb: true
```

### 2. TensorBoard の使用

```bash
# TensorBoardの起動
tensorboard --logdir results/tensorboard
```

## 🐛 トラブルシューティング

### 1. メモリ不足エラー

```bash
# バッチサイズを小さくする
# configs/base_config.yaml
data:
  batch_size: 8  # 16から8に変更
```

### 2. CUDA エラー

```bash
# CPU で実行
export CUDA_VISIBLE_DEVICES=""
python main.py --mode demo
```

### 3. データセットが見つからない

```bash
# データセットのパスを確認
ls data/pascal_voc/
ls data/medical/isic/
```

## 📚 参考資料

- [Pascal VOC 2012 Dataset](http://host.robots.ox.ac.uk/pascal/VOC/voc2012/)
- [ISIC Challenge](https://challenge.isic-archive.com/)
- [U-Net Paper](https://arxiv.org/abs/1505.04597)
- [DeepLabV3+ Paper](https://arxiv.org/abs/1802.02611)

## 🤝 貢献

1. フォークを作成
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成
