"""
Google Colaboratory用セットアップスクリプト
無料枠での動作を最適化
"""

import os
import sys
import subprocess
from pathlib import Path


def setup_colab_environment():
    """Colab環境のセットアップ"""
    print("🔧 Setting up Google Colaboratory environment...")
    
    # Colab環境の検出
    is_colab = 'google.colab' in sys.modules or os.path.exists('/content')
    
    if not is_colab:
        print("⚠️  This script is designed for Google Colaboratory")
        print("   Running in local environment...")
        return False
    
    # 作業ディレクトリの設定
    base_dir = Path('/content/MediSeg-AI')
    base_dir.mkdir(exist_ok=True)
    os.chdir(base_dir)
    
    # 必要なディレクトリの作成
    dirs = ['data', 'uploads', 'models', 'checkpoints']
    for d in dirs:
        (base_dir / d).mkdir(exist_ok=True)
    
    print(f"✅ Working directory: {base_dir}")
    return True


def install_dependencies():
    """依存関係のインストール（Colab最適化）"""
    print("📦 Installing dependencies...")
    
    # Colabに既にインストールされているパッケージを確認
    packages = [
        'torch',
        'torchvision',
        'opencv-python',
        'matplotlib',
        'seaborn',
        'pillow',
        'flask',
        'pyngrok',  # ngrok for Colab
        'gdown',    # Google Drive download
        'requests', # HTTP requests
        'tqdm',     # Progress bars
    ]
    
    # psutilはColab環境で問題がある場合があるので、オプションにする
    try:
        import psutil
        print("✅ psutil is available")
    except ImportError:
        print("⚠️  psutil not available, using fallback monitoring")
        packages.append('psutil')
    
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is already installed")
        except ImportError:
            print(f"📥 Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', package])
            print(f"✅ {package} installed")
    
    print("✅ All dependencies installed")


def setup_ngrok():
    """ngrokのセットアップ（Web GUI公開用）"""
    print("🌐 Setting up ngrok for web access...")
    
    try:
        from pyngrok import ngrok
        print("✅ pyngrok is available")
        return ngrok
    except ImportError:
        print("📥 Installing pyngrok...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', 'pyngrok'])
        from pyngrok import ngrok
        print("✅ pyngrok installed")
        return ngrok


def check_gpu():
    """GPU/TPUの確認"""
    print("🔍 Checking GPU/TPU availability...")
    
    import torch
    
    # GPU確認
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"✅ GPU available: {gpu_name} ({gpu_memory:.1f} GB)")
        return 'cuda'
    
    # TPU確認（Colab Pro/Pro+のみ）
    try:
        import torch_xla
        if torch_xla._XLAC._xla_get_default_device():
            print("✅ TPU available")
            return 'tpu'
    except:
        pass
    
    print("⚠️  No GPU/TPU available, using CPU")
    return 'cpu'


def setup_google_drive():
    """Google Driveのマウント（オプション）"""
    print("📁 Google Drive setup (optional)...")
    
    try:
        from google.colab import drive
        drive.mount('/content/drive')
        print("✅ Google Drive mounted at /content/drive")
        return True
    except ImportError:
        print("⚠️  Google Drive mount skipped (not in Colab)")
        return False
    except Exception as e:
        print(f"⚠️  Google Drive mount failed: {e}")
        return False


def optimize_for_colab():
    """Colab無料枠向けの最適化設定"""
    print("⚙️  Optimizing for Colab free tier...")
    
    # 環境変数の設定
    os.environ['MEDISEG_HOST'] = '0.0.0.0'  # 外部アクセス許可
    os.environ['MEDISEG_PORT'] = '8080'
    os.environ['MEDISEG_DEBUG'] = 'false'
    os.environ['MEDISEG_AUTO_OPEN_BROWSER'] = 'false'  # Colabでは不要
    os.environ['DATA_DIR'] = '/content/MediSeg-AI/data'
    os.environ['MEDISEG_UPLOAD_DIR'] = '/content/MediSeg-AI/uploads'
    
    # メモリ最適化
    import torch
    if torch.cuda.is_available():
        # メモリ効率を最適化
        torch.backends.cudnn.benchmark = True
        # メモリ使用量を削減
        os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'
    
    print("✅ Optimization complete")


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 MediSeg.AI - Google Colaboratory Setup")
    print("=" * 60)
    
    # セットアップ実行
    is_colab = setup_colab_environment()
    install_dependencies()
    device = check_gpu()
    optimize_for_colab()
    
    print("\n" + "=" * 60)
    print("✅ Setup complete!")
    print("=" * 60)
    print(f"Device: {device}")
    print(f"Working directory: {os.getcwd()}")
    print("\nNext steps:")
    print("1. Run: from colab_launcher import launch_web_gui")
    print("2. Or use the Colab notebook: MediSeg_AI_Colab.ipynb")

