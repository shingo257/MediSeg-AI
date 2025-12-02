"""
ヘルスチェック関連ルート
"""

import os
from flask import Blueprint, jsonify
from src.gui.state.app_state import get_app_state

health_bp = Blueprint('health', __name__)


def _import_ok(mod: str) -> bool:
    """モジュールのインポートが可能かチェック"""
    try:
        __import__(mod)
        return True
    except Exception:
        return False


@health_bp.route('/api/healthz')
def healthz():
    """簡易ヘルスチェック: データディレクトリと依存状況を返す"""
    try:
        data_dir = os.environ.get('DATA_DIR', 'data')
        base = os.path.abspath(data_dir)
        os.makedirs(base, exist_ok=True)
        can_write = True
        try:
            test_path = os.path.join(base, '.healthz_write_test')
            with open(test_path, 'w') as f:
                f.write('ok')
            os.remove(test_path)
        except Exception:
            can_write = False
        deps = {
            'pydicom': _import_ok('pydicom'),
            'nibabel': _import_ok('nibabel'),
        }
        return jsonify({
            'success': True, 
            'data_dir': base, 
            'writable': can_write, 
            'deps': deps
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@health_bp.route('/api/version')
def api_version():
    """稼働中アプリのビルド情報を返す（デバッグ用）"""
    app_state = get_app_state()
    import time
    build_info = app_state.build_info.copy()
    build_info['timestamp'] = time.strftime('%Y-%m-%dT%H:%M:%S')
    return jsonify({'success': True, 'build': build_info})

