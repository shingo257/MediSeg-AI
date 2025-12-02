"""
MediSeg.AI - Web-based GUI
カッコイイビジュアルのWebベース医療画像セグメンテーションGUI
"""

import os
import sys
import time
from flask import Flask, render_template
import matplotlib
matplotlib.use('Agg')  # GUIバックエンドを使用
import matplotlib.pyplot as plt
import seaborn as sns

# プロジェクトのパスを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.gui.services.model_service import ModelService
from src.gui.state.app_state import get_app_state
from src.gui.routes import register_blueprints

# Flaskアプリケーション
app = Flask(__name__, 
            template_folder='../../templates',
            static_folder='../../static',
            static_url_path='/static')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Blueprintを登録
register_blueprints(app)

# ダークテーマの設定
plt.style.use('dark_background')
sns.set_theme(style="darkgrid")

# ビルド識別子（稼働中コードの確認用）
app_state = get_app_state()
app_state.build_info = {
    'app': 'MediSeg.AI',
    'version': 'web_gui.samples-real-only',
    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
}

def setup_models():
    """モデルのセットアップ"""
    model_service = ModelService()
    return model_service.setup_models()

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    """Serve a small in-memory favicon to avoid 404s."""
    try:
        from PIL import Image, ImageDraw
        import io
        from flask import send_file
        buf = io.BytesIO()
        img = Image.new('RGBA', (64, 64), (43, 43, 43, 255))
        d = ImageDraw.Draw(img)
        d.ellipse([12, 12, 52, 52], fill=(78, 205, 196, 255))
        img.save(buf, format='PNG')
        buf.seek(0)
        return send_file(buf, mimetype='image/png')
    except Exception:
        return ('', 204)

if __name__ == '__main__':
    from src.gui.launcher import WebGUILauncher
    from src.gui.config import WebGUIConfig
    
    # デバッグモードで起動（直接実行時）
    config = WebGUIConfig(debug=True)
    launcher = WebGUILauncher(config)
    launcher.launch()
