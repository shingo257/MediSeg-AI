"""
セグメンテーション関連ルート
"""

import os
import cv2
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename

from src.gui.services.model_service import ModelService
from src.gui.services.image_service import ImageService
from src.gui.utils.response_utils import error_response, validate_json_request
from src.gui.utils.validation import validate_file_upload
from src.gui.state.app_state import get_app_state

segmentation_bp = Blueprint('segmentation', __name__)

model_service = ModelService()
image_service = ImageService()
app_state = get_app_state()


@segmentation_bp.route('/api/upload', methods=['POST'])
def upload_image():
    """画像のアップロード"""
    is_valid, error_msg, file = validate_file_upload()
    if not is_valid:
        return error_response(error_msg or 'Invalid file upload', 400)
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)
        os.makedirs('uploads', exist_ok=True)
        file.save(filepath)
        
        # 画像の読み込みと表示用のエンコード
        image = cv2.imread(filepath)
        if image is not None:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            app_state.set_current_image(image)
            
            # 画像をBase64エンコード
            image_base64 = image_service.encode_image_to_base64(image)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'image': image_base64,
                'shape': image.shape
            })
        else:
            return error_response('Invalid image file', 400)
    except Exception as e:
        return error_response(str(e), 500)


@segmentation_bp.route('/api/process', methods=['POST'])
def process_image_api():
    """画像処理のAPI"""
    is_valid, error_msg, data = validate_json_request(request, [])
    if not is_valid:
        return error_response(error_msg or 'Invalid request', 400)
    
    model_type = data.get('model', 'U-Net')
    threshold = data.get('threshold', 0.5)
    
    current_image = app_state.get_current_image()
    if current_image is None:
        return error_response('No image loaded', 400)
    
    try:
        # 一時ファイルとして保存
        temp_path = 'temp_image.jpg'
        cv2.imwrite(temp_path, cv2.cvtColor(current_image, cv2.COLOR_RGB2BGR))
        
        # 画像処理
        results, error = model_service.process_image(current_image, model_type, threshold)
        
        # 一時ファイルの削除
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if error:
            return error_response(error, 500)
        
        # 可視化の作成
        visualization = image_service.create_visualization(
            current_image,
            results['prediction'],
            results['binary_mask'],
            results['metrics']
        )
        
        return jsonify({
            'success': True,
            'visualization': visualization,
            'metrics': results['metrics'],
            'model_type': model_type
        })
    except Exception as e:
        return error_response(str(e), 500)


@segmentation_bp.route('/api/download', methods=['GET'])
def download_results():
    """結果のダウンロード"""
    current_results = app_state.get_current_results()
    current_image = app_state.get_current_image()
    
    if current_results is None or current_image is None:
        return error_response('No results available', 400)
    
    try:
        import matplotlib.pyplot as plt
        
        # 結果画像の作成
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.patch.set_facecolor('#2b2b2b')
        
        axes[0].imshow(current_image)
        axes[0].set_title('Original', color='white')
        axes[0].axis('off')
        
        axes[1].imshow(current_results['prediction'], cmap='viridis')
        axes[1].set_title('Prediction', color='white')
        axes[1].axis('off')
        
        axes[2].imshow(current_results['binary_mask'], cmap='gray')
        axes[2].set_title('Binary Mask', color='white')
        axes[2].axis('off')
        
        # ファイルとして保存
        output_path = 'results.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight',
                    facecolor='#2b2b2b', edgecolor='none')
        plt.close()
        
        return send_file(output_path, as_attachment=True, download_name='mediseg_results.png')
    except Exception as e:
        return error_response(str(e), 500)


@segmentation_bp.route('/api/export/metrics', methods=['GET'])
def export_metrics_csv():
    """メトリクスをCSVでダウンロード"""
    current_results = app_state.get_current_results()
    if current_results is None:
        return error_response('No results available', 400)
    
    csv_path = 'metrics.csv'
    metrics = current_results.get('metrics', {})
    try:
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write('metric,value\n')
            for k, v in metrics.items():
                f.write(f'{k},{v}\n')
        return send_file(csv_path, as_attachment=True, download_name='mediseg_metrics.csv')
    except Exception as e:
        return error_response(str(e), 500)

