"""
MediSeg.AI Web GUI Launcher
カッコイイビジュアルのWebベースGUI起動スクリプト
"""

import sys
from src.utils.dependencies import check_and_install_dependencies
from src.gui.launcher import WebGUILauncher

# Web GUIに必要な依存関係
REQUIRED_PACKAGES = ['flask', 'torch', 'opencv-python', 'matplotlib', 'seaborn', 'pillow']

if __name__ == '__main__':
    print("🏥 MediSeg.AI Web GUI Launcher")
    print("=" * 50)
    
    # 依存関係のチェックとインストール
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
        sys.exit(1)
    
    # Web GUIの起動
    try:
        launcher = WebGUILauncher()
        launcher.launch()
    except Exception as e:
        print(f"❌ Failed to start web GUI: {e}")
        sys.exit(1)
