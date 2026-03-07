"""
MediSeg.AI - Web-based GUI
Flask app, error handlers, Blueprint registration. Business logic is in services.
"""

import io
import logging
from pathlib import Path

from flask import Flask, jsonify, send_file

from mediseg_ai.utils.exceptions import (
    ValidationError,
    ModelLoadError,
    DatasetError,
)

logger = logging.getLogger(__name__)

# Repository root (for templates/static paths)
REPO_ROOT = Path(__file__).resolve().parents[3]
TEMPLATES_DIR = REPO_ROOT / "templates"
# Prefer Vite build output if present; fall back to legacy static dir.
STATIC_DIR = (
    REPO_ROOT / "backend" / "gui" / "web" / "static"
    if (REPO_ROOT / "backend" / "gui" / "web" / "static").exists()
    else (REPO_ROOT / "static")
)

# Flaskアプリケーション
app = Flask(
    __name__,
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR),
    static_url_path="/static",
)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size


@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify({'success': False, 'error': str(e)}), 400


@app.errorhandler(FileNotFoundError)
def handle_not_found(e):
    return jsonify({'success': False, 'error': str(e)}), 404


@app.errorhandler(ModelLoadError)
@app.errorhandler(DatasetError)
def handle_mediseg_error(e):
    return jsonify({'success': False, 'error': str(e)}), 500

# Register blueprints
from backend.gui.web.routes.system import bp as system_bp
from backend.gui.web.routes.datasets import bp as datasets_bp
from backend.gui.web.routes.segmentation import bp as segmentation_bp
from backend.gui.web.routes.visualization import bp as visualization_bp
app.register_blueprint(system_bp)
app.register_blueprint(datasets_bp)
app.register_blueprint(segmentation_bp)
app.register_blueprint(visualization_bp)


@app.route('/favicon.ico')
def favicon():
    """Serve a small in-memory favicon to avoid 404s."""
    try:
        from PIL import Image, ImageDraw
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
    from backend.gui.web.launcher import WebGUILauncher
    from backend.gui.web.config import WebGUIConfig
    
    # デバッグモードで起動（直接実行時）
    config = WebGUIConfig(debug=True)
    launcher = WebGUILauncher(config)
    launcher.launch()
