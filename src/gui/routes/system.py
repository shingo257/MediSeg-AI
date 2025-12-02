"""
システム監視関連ルート
"""

from flask import Blueprint, jsonify
from src.utils.system_monitor import system_monitor

system_bp = Blueprint('system', __name__)


@system_bp.route('/api/system/monitoring')
def get_system_monitoring():
    """リアルタイムシステム監視データを取得"""
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
        return jsonify({'success': False, 'error': str(e)}), 500


@system_bp.route('/api/system/detailed')
def get_system_detailed():
    """詳細なシステム情報を取得"""
    try:
        detailed_info = system_monitor.get_detailed_info()
        return jsonify({'success': True, 'data': detailed_info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@system_bp.route('/api/models')
def get_models():
    """利用可能なモデルの取得"""
    from src.gui.services.model_service import ModelService
    model_service = ModelService()
    return jsonify(model_service.get_available_models())

