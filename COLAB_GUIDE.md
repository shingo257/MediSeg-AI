# Google Colaboratory セットアップガイド

MediSeg.AIをGoogle Colaboratoryの無料枠で実行するためのガイドです。

## 📋 目次

1. [前提条件](#前提条件)
2. [クイックスタート](#クイックスタート)
3. [詳細セットアップ](#詳細セットアップ)
4. [トラブルシューティング](#トラブルシューティング)
5. [最適化のヒント](#最適化のヒント)

## 前提条件

- Googleアカウント
- GitHubリポジトリへのアクセス（またはファイルのアップロード）
- （オプション）ngrokアカウント（外部アクセス用）

## クイックスタート

### 方法1: Colabノートブックを使用（推奨）

1. **ノートブックを開く**
   - `MediSeg_AI_Colab.ipynb`をGoogle Colaboratoryで開く
   - または、新しいノートブックを作成して以下のコードを実行

2. **リポジトリのクローン**
```python
!git clone https://github.com/your-username/MediSeg-AI.git /content/MediSeg-AI
```

3. **セットアップの実行**
```python
import os
os.chdir('/content/MediSeg-AI')
!python colab_setup.py
```

4. **Web GUIの起動**
```python
from colab_launcher import launch_web_gui

# ngrokトークン（オプション）を設定
NGROK_TOKEN = ""  # https://dashboard.ngrok.com/get-started/your-authtoken で取得

# Web GUIを起動
launch_web_gui(ngrok_token=NGROK_TOKEN if NGROK_TOKEN else None)
```

5. **アクセス**
   - 表示されたURLにアクセス
   - ngrokトークンがない場合は、Colab内のプレビューリンクを使用

### 方法2: 手動セットアップ

1. **ファイルのアップロード**
   - Colabに `colab_setup.py` と `colab_launcher.py` をアップロード
   - または、GitHubからクローン

2. **セットアップスクリプトの実行**
```python
!python colab_setup.py
```

3. **起動スクリプトの実行**
```python
from colab_launcher import launch_web_gui
launch_web_gui()
```

## 詳細セットアップ

### GPUの有効化

1. **ランタイムタイプの変更**
   - ランタイム > ランタイムのタイプを変更
   - ハードウェアアクセラレータ: **GPU (T4)** を選択

2. **GPUの確認**
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
```

### Google Driveの連携

1. **Driveのマウント**
```python
from google.colab import drive
drive.mount('/content/drive')
```

2. **データの保存**
```python
# モデルやデータセットをDriveに保存
import shutil
shutil.copy('/content/MediSeg-AI/models/model.pth', 
            '/content/drive/MyDrive/MediSeg-AI/models/')
```

3. **Driveから読み込み**
```python
# 次回セッションでDriveから読み込み
shutil.copy('/content/drive/MyDrive/MediSeg-AI/models/model.pth',
            '/content/MediSeg-AI/models/')
```

### ngrokの設定（外部アクセス）

1. **無料アカウントの作成**
   - https://dashboard.ngrok.com/signup でアカウント作成
   - 認証トークンを取得

2. **トークンの設定**
```python
NGROK_TOKEN = "your_ngrok_token_here"
from colab_launcher import launch_web_gui
launch_web_gui(ngrok_token=NGROK_TOKEN)
```

3. **制限事項**
   - 無料枠: 同時接続数1、セッション時間制限あり
   - 有料プラン: より多くの接続と機能

## トラブルシューティング

### GPUが利用できない

**問題**: `torch.cuda.is_available()` が `False` を返す

**解決策**:
1. ランタイム > ランタイムのタイプを変更 > GPU を選択
2. ランタイム > ランタイムの再起動
3. GPU割り当ての待機（無料枠では待機時間がある場合があります）

### メモリ不足エラー

**問題**: `RuntimeError: CUDA out of memory`

**解決策**:
```python
# 1. バッチサイズを小さくする
BATCH_SIZE = 1  # デフォルトより小さく

# 2. 不要な変数を削除
del large_variable
torch.cuda.empty_cache()

# 3. ランタイムを再起動
# ランタイム > ランタイムの再起動
```

### セッションタイムアウト

**問題**: セッションが突然切断される

**解決策**:
1. **定期的な保存**: Google Driveに定期的に保存
2. **自動再接続**: セルを定期的に実行して接続を維持
3. **Colab Pro**: より長いセッション時間（有料）

### ngrok接続エラー

**問題**: ngrokトンネルが作成できない

**解決策**:
1. ngrokトークンが正しく設定されているか確認
2. 無料アカウントの制限を確認（同時接続数など）
3. ポート番号を変更: `launch_web_gui(port=8081)`

### 依存関係のインストールエラー

**問題**: パッケージのインストールに失敗

**解決策**:
```python
# 個別にインストール
!pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
!pip install opencv-python matplotlib seaborn pillow flask pyngrok
```

## 最適化のヒント

### メモリ効率

```python
# 1. 混合精度の使用（GPU使用時）
from torch.cuda.amp import autocast, GradScaler

# 2. 勾配チェックポイント（大規模モデル）
model.gradient_checkpointing_enable()

# 3. 不要なキャッシュのクリア
torch.cuda.empty_cache()
```

### パフォーマンス

```python
# 1. データローダーの最適化
DataLoader(..., num_workers=2, pin_memory=True)

# 2. cuDNNベンチマークの有効化
torch.backends.cudnn.benchmark = True

# 3. バッチサイズの調整
BATCH_SIZE = 4  # GPUメモリに応じて調整
```

### セッション管理

```python
# 1. 定期的なチェックポイント
import time
last_save = time.time()
if time.time() - last_save > 3600:  # 1時間ごと
    save_checkpoint()

# 2. 接続の維持
# セルを定期的に実行（自動実行スクリプトを使用）
```

## 制限事項（無料枠）

- ⏱️ **セッション時間**: 約12時間でタイムアウト
- 💾 **RAM**: 約12.7GB
- 🎮 **GPU**: T4 GPU（利用可能な場合）
- 📊 **GPU使用時間**: 連続使用に制限あり
- 🌐 **ngrok**: 同時接続数1、セッション時間制限

## よくある質問

### Q: 無料でGPUは使えますか？
A: はい、ただし利用可能な場合に限ります。待機時間がある場合があります。

### Q: セッションが切れたらどうなりますか？
A: すべてのデータが失われます。重要なデータはGoogle Driveに保存してください。

### Q: 外部からアクセスできますか？
A: ngrokを使用すれば可能です。無料アカウントで制限があります。

### Q: モデルの訓練はできますか？
A: はい、ただし長時間の訓練はセッションタイムアウトに注意が必要です。

## サポート

問題が解決しない場合は、以下を確認してください：

1. GitHub Issues: https://github.com/your-username/MediSeg-AI/issues
2. ドキュメント: `README.md`
3. ログの確認: エラーメッセージを確認

---

**最終更新**: 2025年1月

