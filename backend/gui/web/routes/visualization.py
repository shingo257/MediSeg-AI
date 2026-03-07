"""Visualization API routes."""
import logging
import numpy as np
from flask import Blueprint, jsonify

from backend.gui.web import state as app_state
from backend.gui.web.services import generate_mask_image, generate_contour_image

logger = logging.getLogger(__name__)
bp = Blueprint('visualization', __name__, url_prefix='/api/visualization')


@bp.route('/multi-view', methods=['GET'])
def get_multi_view():
    """Multi-view image data."""
    if app_state.current_results is None:
        return jsonify({'error': 'No results available'}), 400
    try:
        multi_view_data = {
            'original': app_state.current_image,
            'mask': generate_mask_image(),
            'overlay': app_state.current_results.get('visualization', ''),
            'contour': generate_contour_image()
        }
        return jsonify({'success': True, 'data': multi_view_data})
    except Exception as e:
        logger.exception("Multi-view visualization failed")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/3d', methods=['GET'])
def get_3d_data():
    """3D visualization data."""
    if app_state.current_results is None:
        return jsonify({'error': 'No results available'}), 400
    try:
        prediction = app_state.current_results.get('prediction')
        if prediction is None:
            return jsonify({'error': 'No prediction data available'}), 400
        threshold = 0.5
        mask = prediction > threshold
        y_coords, x_coords = np.where(mask)
        z_coords = prediction[mask] * 100
        if len(y_coords) == 0:
            return jsonify({
                'success': False,
                'error': 'No valid points in prediction',
                'is_fallback': False,
                'fallback_message': '予測結果に有効な点がありません。'
            }), 400
        max_points = 1000
        if len(y_coords) > max_points:
            indices = np.random.choice(len(y_coords), max_points, replace=False)
            y_coords = y_coords[indices]
            x_coords = x_coords[indices]
            z_coords = z_coords[indices]
        points_3d = np.column_stack([x_coords, y_coords, z_coords]).tolist()
        return jsonify({
            'success': True,
            'points': points_3d,
            'is_fallback': False,
            'fallback_message': None
        })
    except Exception as e:
        logger.exception("3D visualization data failed")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/stats', methods=['GET'])
def get_statistics():
    """Statistics data."""
    if app_state.current_results is None:
        return jsonify({'error': 'No results available'}), 400
    try:
        prediction = app_state.current_results.get('prediction')
        binary_mask = app_state.current_results.get('binary_mask')
        confidence_map = None
        if prediction is not None:
            try:
                from scipy import ndimage
                h, w = prediction.shape
                confidence_map = ndimage.zoom(prediction, (32/h, 32/w), order=1).tolist()
            except ImportError:
                h, w = prediction.shape
                target_size = 32
                step_h, step_w = h / target_size, w / target_size
                confidence_map = []
                for i in range(target_size):
                    row = []
                    for j in range(target_size):
                        y = int(i * step_h)
                        x = int(j * step_w)
                        row.append(float(prediction[y, x]) if y < h and x < w else 0.0)
                    confidence_map.append(row)
        region_stats = {}
        if binary_mask is not None:
            total_pixels = binary_mask.size
            lesion_pixels = np.sum(binary_mask > 0)
            background_pixels = total_pixels - lesion_pixels
            region_stats = {
                'background': background_pixels / total_pixels if total_pixels > 0 else 0,
                'lesion': lesion_pixels / total_pixels if total_pixels > 0 else 0,
                'boundary': 0.0
            }
        is_fallback = confidence_map is None or not region_stats
        if confidence_map is None:
            confidence_map = []
        stats_data = {
            'metrics_distribution': app_state.current_results.get('metrics', {}),
            'confidence_map': confidence_map,
            'region_stats': region_stats,
            'timeline_data': [],
            'is_fallback': is_fallback,
            'fallback_message': '⚠️ 一部のデータが利用できません。実データが取得できない場合は空の値が返されます。' if is_fallback else None
        }
        return jsonify({'success': True, 'data': stats_data})
    except Exception as e:
        logger.exception("Get statistics failed")
        return jsonify({'success': False, 'error': str(e)}), 500
