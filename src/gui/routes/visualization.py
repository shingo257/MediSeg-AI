"""
可視化関連ルート
"""

import numpy as np
from flask import Blueprint, jsonify

from src.gui.services.image_service import ImageService
from src.gui.utils.response_utils import error_response
from src.gui.state.app_state import get_app_state

visualization_bp = Blueprint('visualization', __name__)

image_service = ImageService()
app_state = get_app_state()


@visualization_bp.route('/api/visualization/multi-view', methods=['GET'])
def get_multi_view():
    """マルチビュー用の画像データを取得"""
    current_results = app_state.get_current_results()
    current_image = app_state.get_current_image()
    
    if current_results is None or current_image is None:
        return error_response('No results available', 400)
    
    try:
        # 各ビュー用の画像を生成
        multi_view_data = {
            'original': current_image.tolist() if isinstance(current_image, np.ndarray) else current_image,
            'mask': image_service.generate_mask_image(),
            'overlay': image_service.create_visualization(
                current_image,
                current_results.get('prediction'),
                current_results.get('binary_mask'),
                current_results.get('metrics', {})
            ),
            'contour': image_service.generate_contour_image()
        }
        return jsonify({'success': True, 'data': multi_view_data})
    except Exception as e:
        return error_response(str(e), 500)


@visualization_bp.route('/api/visualization/3d', methods=['GET'])
def get_3d_data():
    """3D可視化用のデータを取得"""
    current_results = app_state.get_current_results()
    
    if current_results is None:
        return error_response('No results available', 400)
    
    try:
        prediction = current_results.get('prediction')
        if prediction is None:
            return error_response('No prediction data available', 400)
        
        # 予測結果から3D点群を生成
        threshold = 0.5
        mask = prediction > threshold
        y_coords, x_coords = np.where(mask)
        z_coords = prediction[mask] * 100  # 予測値を高さとして使用
        
        if len(y_coords) == 0:
            return jsonify({
                'success': False,
                'error': 'No valid points in prediction',
                'is_fallback': False,
                'fallback_message': '予測結果に有効な点がありません。'
            }), 400
        
        # 点をサンプリング（多すぎる場合は間引き）
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
        return error_response(str(e), 500)


@visualization_bp.route('/api/visualization/stats', methods=['GET'])
def get_statistics():
    """統計データを取得"""
    current_results = app_state.get_current_results()
    
    if current_results is None:
        return error_response('No results available', 400)
    
    try:
        prediction = current_results.get('prediction')
        binary_mask = current_results.get('binary_mask')
        
        # 実データから統計を計算
        confidence_map = None
        if prediction is not None:
            # 予測結果を32x32にリサンプリングして信頼度マップを生成
            try:
                from scipy import ndimage
                h, w = prediction.shape
                confidence_map = ndimage.zoom(prediction, (32/h, 32/w), order=1).tolist()
            except ImportError:
                # scipyが利用できない場合は、シンプルなリサンプリングを使用
                h, w = prediction.shape
                target_size = 32
                step_h, step_w = h / target_size, w / target_size
                confidence_map = []
                for i in range(target_size):
                    row = []
                    for j in range(target_size):
                        y = int(i * step_h)
                        x = int(j * step_w)
                        row.append(float(prediction[y, x]))
                    confidence_map.append(row)
        
        # バイナリマスクから統計を計算
        region_stats = []
        if binary_mask is not None:
            # 簡易的な領域統計（実際の実装ではより詳細な分析が可能）
            total_pixels = binary_mask.size
            positive_pixels = np.sum(binary_mask > 0)
            coverage = float(positive_pixels / total_pixels) if total_pixels > 0 else 0.0
            
            region_stats = [{
                'region': 'all',
                'coverage': coverage,
                'pixels': int(positive_pixels)
            }]
        
        return jsonify({
            'success': True,
            'confidence_map': confidence_map,
            'region_stats': region_stats,
            'is_fallback': False
        })
    except Exception as e:
        return error_response(str(e), 500)

