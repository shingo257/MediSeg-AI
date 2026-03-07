# Colab での学習手順書（MediSeg.AI）

Google Colab 上で MediSeg.AI の**学習（訓練）**を実行するための具体的な手順です。

---

## 1. データセットはダウンロードできるか

### 1.1 まとめ

| データセット | 自動取得 | 学習コマンド | 備考 |
|-------------|----------|--------------|------|
| **medical_small** | ✅ **可能（合成生成）** | `train-medical` | ネット不要。Colab で確実に使える。 |
| **isic_2018 / isic_2019** | ⚠️ URL から取得可能 | `train-medical` | 公開URLあり。容量大・時間かかる場合あり。 |
| **pascal_voc_2012** | ⚠️ URL から取得可能 | `train` | ミラーURLあり。展開後のパスに注意。 |
| **coco_sample** | ⚠️ URL から取得可能 | — | セグメンテーション用マスクは含まないため、本プロジェクトの学習には未対応。 |

- **確実にそのまま使えるのは `medical_small`（合成データ）のみ**です。Colab ではまずこれを推奨します。
- 上記以外（ISIC 公式サイトから手動取得など）は [DATASET_GUIDE.md](../DATASET_GUIDE.md) を参照してください。

### 1.2 medical_small（合成）について

- **ダウンロード**: 不要。Colab 上で `RealDatasetDownloader.download_dataset("medical_small")` を実行すると、その場で**合成医療画像とマスク**が生成されます。
- **保存先**: `data/medical_small/images` と `data/medical_small/masks` が自動作成されます。
- **train-medical**: このパスを `--data-dir` に指定すればそのまま学習できます。

### 1.3 ISIC / Pascal VOC を URL から取得する場合

- **RealDatasetDownloader** で `download_dataset("isic_2018")` や `download_dataset("pascal_voc_2012")` を実行すると、定義されている URL からダウンロードを試みます。
- 公開URLの変更・アクセス制限・Colab のネット環境により、**失敗することがあります**。その場合は公式サイトから手動ダウンロードし、所定のディレクトリ構造で配置してください。
- ISIC で学習する場合: 配置後は `root_dir` の直下に `images/` と `masks/` がある形にします（足りない場合はリネームやシンボリックリンクで合わせる）。
- Pascal VOC で学習する場合: `train` の `--data-dir` には、`JPEGImages` と `SegmentationClass` がある **VOC2012 のディレクトリ**（例: `.../VOCdevkit/VOC2012`）を指定します。

---

## 2. Colab での学習の流れ（最小手順）

### ステップ 1: リポジトリのクローンとセットアップ

ノートブックで次を実行します（`REPO_URL` は自分のリポジトリに書き換えてください）。

```python
REPO_URL = "https://github.com/あなたのユーザー名/MediSeg-AI.git"
REPO_DIR = "/content/MediSeg-AI"

import os
if not os.path.exists(REPO_DIR):
    !git clone {REPO_URL} {REPO_DIR}

%cd {REPO_DIR}
import sys
sys.path.insert(0, REPO_DIR)
!python colab_setup.py
```

### ステップ 2: GPU の有効化

メニュー **「ランタイム」→「ランタイムのタイプを変更」** で **GPU** を選択し、ランタイムを再起動します。

### ステップ 3: データの準備（medical_small を使う場合）

合成データならネット不要で確実に用意できます。

```python
from mediseg_ai.data_loaders.real_datasets import RealDatasetDownloader

data_dir = "/content/MediSeg-AI/data"
downloader = RealDatasetDownloader(data_dir=data_dir)
downloader.download_dataset("medical_small")
```

実行後、`/content/MediSeg-AI/data/medical_small/images` と `masks` ができていれば成功です。

### ステップ 4: 学習の実行（train-medical）

```python
!python main.py train-medical \
  --data-dir /content/MediSeg-AI/data/medical_small \
  --save-dir /content/MediSeg-AI/results
```

- デフォルトで 150 epoch 程度まで回ります。Colab の制限に合わせて、設定で epoch 数を減らしても構いません。
- 結果は `--save-dir` 以下に保存されます。

### ステップ 5: 結果の保存（任意）

セッション終了後も残したい場合は、Google Drive にコピーします。

```python
from google.colab import drive
drive.mount("/content/drive")

import shutil
save_dir = "/content/MediSeg-AI/results"
drive_dir = "/content/drive/MyDrive/MediSeg-AI/results"
os.makedirs(drive_dir, exist_ok=True)
for f in os.listdir(save_dir):
    shutil.copy(os.path.join(save_dir, f), os.path.join(drive_dir, f))
print("Saved to Drive:", drive_dir)
```

---

## 3. 手順を 1 セルでまとめた例

以下を Colab の 1 つのコードセルに貼り、**ステップ 1（クローン・セットアップ）を済ませたあと**に実行すると、medical_small で一通り学習できます。

```python
# セットアップ済みであること: クローン & colab_setup.py 実行済み
import os
import sys
REPO_DIR = "/content/MediSeg-AI"
os.chdir(REPO_DIR)
if REPO_DIR not in sys.path:
    sys.path.insert(0, REPO_DIR)

# 1) 合成データを準備
from mediseg_ai.data_loaders.real_datasets import RealDatasetDownloader
downloader = RealDatasetDownloader(data_dir=os.path.join(REPO_DIR, "data"))
downloader.download_dataset("medical_small")

# 2) 学習実行
!python main.py train-medical \
  --data-dir {REPO_DIR}/data/medical_small \
  --save-dir {REPO_DIR}/results
```

---

## 4. 他のデータセットで学習する場合

### 4.1 ISIC（isic_2018 など）をダウンロードして使う

```python
from mediseg_ai.data_loaders.real_datasets import RealDatasetDownloader

downloader = RealDatasetDownloader(data_dir="/content/MediSeg-AI/data")
downloader.download_dataset("isic_2018")  # または "isic_2019"
```

- ダウンロード・展開後、**`images` と `masks` が同じルート直下にあるディレクトリ**を `--data-dir` に指定する必要があります。
- 展開先が `ISIC2018_Task1-2_Training_Input` のような名前の場合は、その親ディレクトリを `--data-dir` にし、中身が `images/` と `masks/` になるようリネームするか、パスを合わせてください。

```python
# 例: 展開後のディレクトリ構造を images/masks に合わせた場合
!python main.py train-medical \
  --data-dir /content/MediSeg-AI/data/isic_2018 \
  --save-dir /content/MediSeg-AI/results
```

### 4.2 Pascal VOC で学習する（train）

```python
downloader = RealDatasetDownloader(data_dir="/content/MediSeg-AI/data")
downloader.download_dataset("pascal_voc_2012")
```

展開後、`VOCdevkit/VOC2012` のパスを `--data-dir` に指定します。

```python
!python main.py train \
  --data-dir /content/MediSeg-AI/data/pascal_voc_2012/VOCdevkit/VOC2012 \
  --save-dir /content/MediSeg-AI/results
```

---

## 5. よくあるトラブル

| 現象 | 対処 |
|------|------|
| `KeyError: 'isic'` など | 先に `colab_setup.py` を実行し、`sys.path.insert(0, REPO_DIR)` でリポジトリをパスに含める。 |
| データが 0 件 | `medical_small` の場合は `download_dataset("medical_small")` が正常終了しているか確認。ISIC の場合は `images/` と `masks/` の対応とパスを確認。 |
| メモリ不足 | バッチサイズを小さくする（設定で `batch_size` を 4 や 2 に）。ランタイムを再起動してから再実行。 |
| セッションが切れた | 学習結果は `/content` にのみあるため消えます。重要な結果はステップ 5 のように Drive にコピーする。 |

---

## 6. 関連ドキュメント

- [COLAB.md](COLAB.md) — Colab の基本（Web GUI 起動など）
- [DATASET_GUIDE.md](../DATASET_GUIDE.md) — データセット一覧と手動取得
- [USAGE.md](../USAGE.md) — ローカル環境での訓練コマンド
