"""System and health API routes."""
import os
import logging
from flask import Blueprint, jsonify

from backend.gui.web.state import DATA_DIR, BUILD_INFO
from mediseg_ai.utils.system_monitor import system_monitor

logger = logging.getLogger(__name__)
bp = Blueprint('system', __name__, url_prefix='/api')


def _import_ok(mod: str) -> bool:
    """Return True if module can be imported, False otherwise (used for healthz deps)."""
    try:
        __import__(mod)
        return True
    except Exception:
        return False


@bp.route('/healthz')
def healthz():
    """Health check: data dir and deps."""
    try:
        base = os.path.abspath(DATA_DIR)
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
        return jsonify({'success': True, 'data_dir': base, 'writable': can_write, 'deps': deps})
    except Exception as e:
        logger.exception("Health check failed")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/version')
def api_version():
    """Build info."""
    return jsonify({'success': True, 'build': BUILD_INFO})


@bp.route('/system/monitoring')
def get_system_monitoring():
    """System monitoring metrics."""
    try:
        metrics = system_monitor.get_system_metrics()
        return jsonify({
            'success': True,
            'cpu_usage': metrics['cpu_usage'],
            'memory_usage': metrics['memory_usage'],
            'gpu_usage': metrics['gpu_usage'],
            'gpu_memory_usage': metrics['gpu_memory_usage'],
            'gpu_available': metrics['gpu_available'],
            'processing_speed': metrics['processing_speed']
        })
    except Exception as e:
        logger.exception("System monitoring failed")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/system/detailed')
def get_system_detailed():
    """Detailed system info."""
    try:
        detailed_info = system_monitor.get_detailed_info()
        return jsonify({'success': True, 'data': detailed_info})
    except Exception as e:
        logger.exception("System detailed info failed")
        return jsonify({'success': False, 'error': str(e)}), 500
