"""
MediSeg.AI GUI Launcher
カッコイイビジュアルの医療画像セグメンテーションGUI起動スクリプト
"""

import sys
import os

# プロジェクトのパスを追加
sys.path.append('src')

from src.utils.dependencies import check_and_install_dependencies

# PyQt5 GUIに必要な依存関係
REQUIRED_PACKAGES = [
    'PyQt5',
    'matplotlib',
    'seaborn',
    'torch',
    'torchvision',
    'opencv-python',
    'numpy',
    'scikit-image'
]

def main():
    """メイン関数"""
    print("=" * 60)
    print("🚀 MediSeg.AI GUI Launcher")
    print("=" * 60)
    
    # 依存関係のチェックとインストール
    print("Checking dependencies...")
    success, missing = check_and_install_dependencies(
        REQUIRED_PACKAGES,
        auto_install=True,
        verbose=True
    )
    
    if not success:
        print("❌ Failed to install required dependencies")
        if missing:
            print("Please install the following packages manually:")
            for package in missing:
                print(f"  pip install {package}")
        return
    else:
        print("✅ All dependencies are available!")
    
    # GUIの起動
    print("\n🎨 Launching MediSeg.AI GUI...")
    try:
        from src.gui.main_window import main as gui_main
        gui_main()
    except Exception as e:
        print(f"❌ Failed to launch GUI: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed")
        print("2. Check if PyQt5 is properly installed")
        print("3. Try running: pip install PyQt5 matplotlib seaborn")

if __name__ == "__main__":
    main()

