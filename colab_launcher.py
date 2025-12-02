"""
Google Colaboratory用Web GUI起動スクリプト
ngrokを使用してWeb GUIを外部公開
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path


def launch_web_gui(ngrok_token=None, port=8080):
    """
    Web GUIを起動してngrokで公開
    
    Args:
        ngrok_token: ngrok認証トークン（オプション、無料アカウントで取得可能）
        port: Flaskアプリのポート番号
    """
    print("🚀 Launching MediSeg.AI Web GUI on Google Colaboratory...")
    
    # Colab環境の確認
    is_colab = 'google.colab' in sys.modules or os.path.exists('/content')
    if not is_colab:
        print("⚠️  This launcher is designed for Google Colaboratory")
        print("   For local use, use: python web_gui_launcher.py")
        return
    
    # 環境変数の設定
    os.environ['MEDISEG_HOST'] = '0.0.0.0'
    os.environ['MEDISEG_PORT'] = str(port)
    os.environ['MEDISEG_DEBUG'] = 'false'
    os.environ['MEDISEG_AUTO_OPEN_BROWSER'] = 'false'
    
    # ngrokのセットアップ
    try:
        from pyngrok import ngrok, conf
        
        # ngrok認証トークンの設定（オプション）
        if ngrok_token:
            conf.get_default().auth_token = ngrok_token
            print("✅ ngrok token configured")
        else:
            print("⚠️  No ngrok token provided. Using free tier (limited)")
            print("   Get a free token at: https://dashboard.ngrok.com/get-started/your-authtoken")
        
        # ngrokトンネルの作成
        print(f"🌐 Creating ngrok tunnel on port {port}...")
        public_url = ngrok.connect(port)
        print(f"\n{'='*60}")
        print(f"✅ Public URL: {public_url}")
        print(f"🌐 Access your Web GUI at: {public_url}")
        print(f"{'='*60}\n")
        
    except ImportError:
        print("❌ pyngrok not installed. Installing...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', 'pyngrok'])
        from pyngrok import ngrok, conf
        if ngrok_token:
            conf.get_default().auth_token = ngrok_token
        public_url = ngrok.connect(port)
        print(f"✅ Public URL: {public_url}")
    
    except Exception as e:
        print(f"⚠️  ngrok setup failed: {e}")
        print("   Using localhost only (not accessible from outside)")
        public_url = None
    
    # Web GUIの起動
    try:
        print("\n🎨 Starting MediSeg.AI Web GUI...")
        print("=" * 60)
        
        # プロジェクトパスの追加
        if os.path.exists('/content/MediSeg-AI'):
            sys.path.insert(0, '/content/MediSeg-AI')
        else:
            sys.path.insert(0, os.getcwd())
        
        from src.gui.launcher import WebGUILauncher
        
        # ランチャーの作成と起動
        launcher = WebGUILauncher()
        
        # 別スレッドでFlaskアプリを起動
        def run_flask():
            launcher.launch()
        
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        # 起動待機
        time.sleep(5)
        
        print("\n" + "=" * 60)
        print("✅ MediSeg.AI Web GUI is running!")
        print("=" * 60)
        if public_url:
            print(f"\n🌐 Public URL (Access from anywhere):")
            print(f"   {public_url}")
            print(f"\n📱 Click the link above or copy it to your browser")
        else:
            print(f"\n🔗 Local URL (Colab only):")
            print(f"   http://localhost:{port}")
            print("⚠️  Not accessible from outside (ngrok not configured)")
            print("   To enable external access, set NGROK_TOKEN in the notebook")
        print("\n💡 Important Tips:")
        print("   ⚠️  Keep this cell running to maintain the connection")
        print("   ⏱️  Colab free tier sessions timeout after ~12 hours")
        print("   💾 Save your work regularly to Google Drive")
        print("   🔄 If connection drops, restart this cell")
        print("=" * 60)
        
        # メインスレッドをブロックしてFlaskアプリを維持
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            if public_url:
                ngrok.kill()
            launcher.cleanup()
    
    except Exception as e:
        print(f"❌ Failed to launch Web GUI: {e}")
        import traceback
        traceback.print_exc()
        if public_url:
            ngrok.kill()


def launch_with_drive_sync(drive_path='/content/drive/MyDrive/MediSeg-AI', ngrok_token=None):
    """
    Google Driveと同期して起動
    
    Args:
        drive_path: Google Drive内のパス
        ngrok_token: ngrok認証トークン
    """
    print("📁 Setting up Google Drive sync...")
    
    # Google Driveのマウント
    try:
        from google.colab import drive
        drive.mount('/content/drive')
        print(f"✅ Google Drive mounted")
    except:
        print("⚠️  Google Drive mount failed or not in Colab")
        drive_path = None
    
    # データの同期
    if drive_path and os.path.exists(drive_path):
        print(f"📂 Syncing with: {drive_path}")
        # モデルやデータセットをDriveからコピー
        # 実装は必要に応じて追加
    
    # Web GUIの起動
    launch_web_gui(ngrok_token=ngrok_token)


if __name__ == '__main__':
    # コマンドライン引数の処理
    import argparse
    parser = argparse.ArgumentParser(description='Launch MediSeg.AI Web GUI on Colab')
    parser.add_argument('--ngrok-token', type=str, help='ngrok authentication token')
    parser.add_argument('--port', type=int, default=8080, help='Port number')
    parser.add_argument('--drive-sync', action='store_true', help='Enable Google Drive sync')
    parser.add_argument('--drive-path', type=str, default='/content/drive/MyDrive/MediSeg-AI', 
                       help='Google Drive path')
    
    args = parser.parse_args()
    
    if args.drive_sync:
        launch_with_drive_sync(drive_path=args.drive_path, ngrok_token=args.ngrok_token)
    else:
        launch_web_gui(ngrok_token=args.ngrok_token, port=args.port)

