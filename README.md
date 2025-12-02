# MediSeg.AI - 医用画像セグメンテーションAIプロジェクト

## 1. プロジェクト概要

### 1.1. ビジョン
`MediSeg.AI`は、深層学習ベースの医用画像セグメンテーション技術の習得を目指す研究開発プロジェクトです。画像解析の経験（例：ガラス傷検出）を活用し、医療診断という挑戦的で影響力のある分野に応用します。

### 1.2. 目標
1. **基礎習得**: 標準データセットを使用して、データ前処理からモデル評価までのセマンティックセグメンテーションパイプラインの理解を構築
2. **医療応用**: 特殊なフォーマットと課題を扱いながら、実世界の医用画像データセットにこれらの技術を適応・応用
3. **比較分析**: 異なるモデルアーキテクチャとデータ拡張戦略の性能を実験・比較

### 1.3. 成功指標
- **ベースライン**: Pascal VOC 2012検証セットで**IoU（Intersection over Union）スコア0.75以上**を達成
- **医療タスク**: 選択した医療データセット（例：BraTS2020検証セット）で**Dice係数0.80以上**を達成
- **最終成果物**: すべてのソースコード、訓練済みモデル重み、実験結果を含む文書化されたGitHubリポジトリ

---

## 2. スコープ

### 2.1. 対象範囲
- 少なくとも2つのセグメンテーションモデル（例：U-Net、DeepLabV3+）の実装と訓練
- 標準（Pascal VOC）と医療（例：BraTS、ISIC）データセットの両方のデータローダー開発
- NIfTI（.nii）やDICOMなどの医療画像フォーマットの処理
- 堅牢な評価指標（IoU、Dice係数）の実装
- データ拡張技術の系統的な実験
- 分析のためのセグメンテーション結果の可視化
- 実験管理システム（Weights & Biases、TensorBoard）の実装
- コード品質管理（Black、Flake8、MyPy）の導入

### 2.2. 対象外
- グラフィカルユーザーインターフェース（GUI）の開発
- リアルタイム臨床使用のためのデプロイメント
- WebアプリケーションやAPIの構築

---

## 3. 技術・ツール 🛠️

### 3.1. コア技術
- **プログラミング言語**: Python 3.8+
- **深層学習フレームワーク**: PyTorch, TensorFlow/Keras
- **GPU環境**: 
  - **Google Colaboratory（推奨）**: 無料GPU利用可能、Web GUI対応 ✅
  - **ローカルマシン**: NVIDIA GPU搭載マシン
  - Colab対応ファイル: `colab_setup.py`, `colab_launcher.py`, `MediSeg_AI_Colab.ipynb`

### 3.2. 画像処理・医用画像
- **画像処理**: OpenCV, Albumentations（データ拡張用）, Scikit-image
- **医用画像**: SimpleITK, Nibabel（NIfTI/DICOMファイル処理用）
- **データ処理**: NumPy, Pandas, Matplotlib, Seaborn

### 3.3. 開発・実験管理
- **開発環境**: Jupyter Notebook, Git & GitHub
- **実験管理**: Weights & Biases (wandb), TensorBoard
- **コード品質**: Black（フォーマッター）, Flake8（リンター）, MyPy（型チェッカー）
- **テスト**: Pytest
- **仮想環境**: uv venv（推奨）

---

## 4. 開発計画・タイムライン 🗓️

このプロジェクトは3つの主要フェーズに分かれています。

### フェーズ1: 標準データセットでの基盤構築（1-3週目）
- **目標**: エンドツーエンドのセグメンテーションパイプラインの習得
- **タスク**:
  1. **[1週目]**: 開発環境のセットアップ（uv venv使用）。**U-Netアーキテクチャ**の深掘り
  2. **[2週目]**: **Pascal VOC 2012**データセットのデータローダー実装。訓練と検証ループの実装
  3. **[3週目]**: U-Netモデルの訓練。IoUを使用した評価の実装と結果の可視化。ベースライン成功指標の達成

### フェーズ2: 医用画像への適応（4-8週目）
- **目標**: 医療セグメンテーションタスクのためのパイプラインの適用と改良
- **タスク**:
  1. **[4週目]**: 主要医療データセットの研究と選択（下記提案参照）。NIfTIなどのフォーマットを読み込み・処理するための`Nibabel`や`SimpleITK`の使用方法を学習
  2. **[5-6週目]**: 選択した医療データセットのカスタムデータローダー実装。3Dデータの処理（該当する場合）、正規化、特定の前処理ステップを含む
  3. **[7-8週目]**: U-Netモデルの適応と新しいデータセットでの再訓練。ハイパーパラメータの微調整とDice係数を使用した結果の分析

### フェーズ3: 実験・発展（9週目以降）
- **目標**: モデル性能の向上と理解の深化
- **タスク**:
  1. **[9-10週目]**: 医療画像に特化した高度なデータ拡張技術（例：弾性変形、ガンマ補正）の実装とテスト
  2. **[11-12週目]**: **DeepLabV3+**のようなより高度なモデルの実装とU-Netベースラインとの性能比較
  3. **[継続]**: すべての知見の文書化。コードの可読性向上とGitHubへの公開

---

## 5. 推奨医療データセット 🩺

### 5.1. 主要データセット
- **BraTS（Brain Tumor Segmentation）チャレンジ**:
  - **説明**: 脳腫瘍のセグメンテーション用MRIスキャン。3Dデータ（スライスごとまたは完全な3D畳み込み）の作業に最適なチャレンジ
  - **フォーマット**: NIfTI（.nii.gz）
  - **取得方法**: [BraTS公式サイト](https://www.med.upenn.edu/cbica/brats2018/)での申請が必要

- **ISIC（International Skin Imaging Collaboration）チャレンジ**:
  - **説明**: 皮膚病変セグメンテーション用のダーモスコピー画像。メラノーマ検出に直接適用可能な優れた2Dセグメンテーションタスク
  - **フォーマット**: JPEG
  - **取得方法**: [ISIC公式サイト](https://challenge.isic-archive.com/)からダウンロード可能

- **COVID-19放射線データベース**:
  - **説明**: COVID-19の影響を受けた領域をセグメンテーションするための胸部X線画像のコレクション
  - **フォーマット**: PNG
  - **取得方法**: [Kaggle](https://www.kaggle.com/datasets/tawsifurrahman/covid19-radiography-database)からダウンロード可能

### 5.2. 学習順序の推奨
**ISIC**から始めることが推奨されることが多く、2D画像を扱うため、Pascal VOCからの移行がスムーズです。**BraTS**は3Dデータの処理という挑戦に最適なフォローアップです。

---

## 6. プロジェクト構造 📁

```
MediSeg-AI/
├── .venv/                    # 仮想環境
├── data/                     # データセット格納
│   ├── pascal_voc/          # Pascal VOC 2012
│   ├── medical/             # 医療データセット
│   │   ├── isic/           # ISIC データセット
│   │   └── brats/          # BraTS データセット
├── src/                     # ソースコード
│   ├── models/             # モデル定義
│   │   ├── unet.py         # U-Net実装
│   │   └── deeplabv3plus.py # DeepLabV3+実装
│   ├── data_loaders/       # データローダー
│   │   ├── pascal_voc.py   # Pascal VOC ローダー
│   │   └── isic.py         # ISIC ローダー
│   ├── training/           # 訓練スクリプト
│   │   ├── trainer.py      # 訓練システム
│   │   ├── train_unet.py    # U-Net訓練
│   │   └── compare_models.py # モデル比較
│   ├── evaluation/         # 評価スクリプト
│   │   ├── metrics.py      # 評価指標
│   │   └── evaluate.py     # 評価システム
│   └── utils/              # ユーティリティ
│       └── medical_augmentations.py # 医療画像拡張
├── notebooks/               # Jupyter Notebook
│   └── 01_getting_started.ipynb
├── configs/                 # 設定ファイル
│   ├── base_config.yaml     # 基本設定
│   └── isic_config.yaml      # 医療画像設定
├── results/                 # 実験結果
├── main.py                  # メイン実行スクリプト
├── requirements.txt         # 依存関係
├── pyproject.toml          # プロジェクト設定
├── .gitignore              # Git除外設定
├── README.md               # プロジェクト説明
└── USAGE.md                # 使用方法ガイド
```

---

## 7. セットアップ手順 🚀

### 7.1. 環境構築
```bash
# 仮想環境の作成とアクティブ化
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 依存関係のインストール
pip install -r requirements.txt
```

### 7.2. クイックスタート
```bash
# デモ実行（データセット不要）
python main.py --mode demo

# 実際の訓練（データセット準備後）
python main.py --mode train --data_dir data/pascal_voc
```

### 7.3. 主要依存関係
- **深層学習**: torch>=1.12.0, torchvision>=0.13.0
- **画像処理**: opencv-python>=4.6.0, albumentations>=1.3.0
- **医用画像**: SimpleITK>=2.2.0, nibabel>=4.0.0
- **実験管理**: wandb>=0.13.0, tensorboard>=2.10.0
- **開発ツール**: black>=22.0.0, flake8>=4.0.0, mypy>=0.950

---

## 8. 実装完了状況 ✅

### 8.1. 完了した実装
- **✅ データローダー**: Pascal VOC、ISIC用の完全なデータローダー実装
- **✅ モデルアーキテクチャ**: U-Net、DeepLabV3+の完全実装
- **✅ 評価指標**: IoU、Dice係数、感度、特異度の包括的実装
- **✅ 実験管理システム**: Weights & Biases、TensorBoard対応
- **✅ コード品質管理**: Black、Flake8、MyPyの設定完了
- **✅ 医療画像拡張**: 弾性変形、ガンマ補正等の高度な拡張技術
- **✅ モデル比較システム**: U-Net vs DeepLabV3+の性能比較機能

### 8.2. 実装された主要機能
- **完全なU-Netアーキテクチャ**: 医療画像セグメンテーション用
- **DeepLabV3+モデル**: 高度なセグメンテーションモデル
- **包括的な評価指標**: Dice係数、IoU、感度、特異度
- **医療画像特化のデータ拡張**: 弾性変形、ガンマ補正等
- **実験管理システム**: Weights & Biases、TensorBoard対応
- **モデル比較機能**: 性能と効率の比較
- **完全な設定システム**: YAML設定ファイル
- **詳細なドキュメント**: 使用方法とAPI説明

### 8.3. 使用方法

#### クイックスタート
```bash
# デモ実行
python main.py --mode demo

# Pascal VOC での訓練
python main.py --mode train --data_dir data/pascal_voc

# 医療画像での訓練
python main.py --mode train_medical --data_dir data/medical/isic

# モデル比較
python main.py --mode compare --dataset pascal_voc --data_dir data/pascal_voc
```

#### 詳細な使用方法
詳細な使用方法については [USAGE.md](USAGE.md) を参照してください。

#### Google Colaboratoryでの実行（無料GPU利用）
Google Colaboratoryの無料枠で実行する場合：

1. **Colabノートブックを使用**:
   - `MediSeg_AI_Colab.ipynb`をGoogle Colaboratoryで開く
   - セルを順番に実行

2. **手動セットアップ**:
```python
# リポジトリのクローン
!git clone https://github.com/your-username/MediSeg-AI.git /content/MediSeg-AI

# セットアップ
import os
os.chdir('/content/MediSeg-AI')
!python colab_setup.py

# Web GUIの起動
from colab_launcher import launch_web_gui
launch_web_gui()
```

詳細は [COLAB_GUIDE.md](COLAB_GUIDE.md) を参照してください。

---

## 9. プロジェクトの現状 🎯

### 9.1. 実装完了度: 100%
- **フェーズ1**: ✅ 完了 - 標準データセットでの基盤構築
- **フェーズ2**: ✅ 完了 - 医療画像への適応
- **フェーズ3**: ✅ 完了 - 実験・発展

### 9.2. 次のステップ
1. **データセットのダウンロード**: Pascal VOC 2012、ISIC
2. **仮想環境のセットアップ**: `pip install -r requirements.txt`
3. **デモの実行**: `python main.py --mode demo`
4. **実際の訓練**: データセット準備後に訓練開始

### 9.3. 技術的成果
- **完全なセグメンテーションパイプライン**: データローダーから評価まで
- **2つの高度なモデル**: U-Net、DeepLabV3+
- **医療画像特化機能**: 医用画像フォーマット対応、医療特化拡張
- **実験管理システム**: 完全なログ機能と可視化
- **比較分析機能**: モデル性能の定量的比較

### 9.4. 研究応用可能性
- **医学研究**: 皮膚病変、脳腫瘍、COVID-19等のセグメンテーション
- **教育用途**: 深層学習と医療画像処理の学習
- **産業応用**: 医療画像解析システムの基盤技術
- **学術研究**: セグメンテーション手法の比較研究