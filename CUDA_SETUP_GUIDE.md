# CUDA セットアップガイド

## GPU使用率監視を有効にするためのCUDAセットアップ

### 1. NVIDIA GPUドライバーの確認
```bash
nvidia-smi
```
このコマンドでNVIDIA GPUが認識されているか確認してください。

### 2. CUDA Toolkitのインストール
- [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)から最新版をダウンロード
- Windows 11/10用のインストーラーを実行
- インストール後、環境変数が自動設定されることを確認

### 3. PyTorch with CUDA のインストール
現在のPyTorchがCPU版の場合、CUDA版に変更：

```bash
# 現在のPyTorchをアンインストール
pip uninstall torch torchvision torchaudio

# CUDA版PyTorchをインストール（CUDA 11.8の場合）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# または CUDA 12.1の場合
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**uv を使う場合**（プロジェクトで uv を標準にしている場合）は、`uv run` の前に CUDA 版 PyTorch を入れます：

```bash
# CUDA 11.8 の場合
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# または CUDA 12.1 の場合
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 4. CUDA動作確認
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA device count: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"Current device: {torch.cuda.current_device()}")
    print(f"Device name: {torch.cuda.get_device_name(0)}")
```

### 5. トラブルシューティング

#### 問題: `torch.cuda.is_available()` が False を返す
**解決策:**
1. NVIDIAドライバーが最新か確認
2. CUDA Toolkitが正しくインストールされているか確認
3. PyTorchがCUDA版か確認: `torch.version.cuda`

#### 問題: GPU使用率が0%のまま
**解決策:**
1. GPUが実際に使用されているか確認: `nvidia-smi`
2. PyTorchでGPUテンソルを作成してテスト:
```python
import torch
x = torch.randn(1000, 1000).cuda()
print(f"GPU memory allocated: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
```

### 6. 代替案: CPU版での動作
CUDAが利用できない場合でも、MediSeg.AIはCPU版で完全に動作します：
- リアルタイム監視で「未接続」と表示
- セグメンテーション処理はCPUで実行
- パフォーマンスは低下しますが、機能は利用可能

### 7. 推奨システム要件
- **GPU**: NVIDIA GeForce GTX 1060以上（6GB VRAM以上推奨）
- **RAM**: 16GB以上
- **OS**: Windows 10/11, Ubuntu 18.04以上
- **CUDA**: 11.8以上

### 8. パフォーマンス最適化
CUDAが利用可能な場合の推奨設定：
```python
# バッチサイズを調整
BATCH_SIZE = 4  # GPU VRAMに応じて調整

# 混合精度学習を有効化
torch.backends.cudnn.benchmark = True
```

## 注意事項
- CUDAのインストールには管理者権限が必要な場合があります
- 古いGPUでは最新のCUDA Toolkitがサポートされない場合があります
- 仮想環境を使用している場合は、CUDA Toolkitをグローバルにインストールする必要があります
