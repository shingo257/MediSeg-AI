"""
データセット関連ルート
"""

import os
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename

from src.gui.services.dataset_service import DatasetService
from src.gui.services.download_service import DownloadService
from src.gui.utils.response_utils import success_response, error_response, validate_json_request
from src.gui.utils.validation import validate_file_upload, validate_dataset_id
from src.gui.utils.image_utils import has_any_images

datasets_bp = Blueprint('datasets', __name__)

# サービスインスタンス（データディレクトリは環境変数から取得）
DATA_DIR = os.environ.get('DATA_DIR', 'data')
dataset_service = DatasetService(data_dir=DATA_DIR)
download_service = DownloadService(data_dir=DATA_DIR)


@datasets_bp.route('/api/datasets/list')
def list_datasets():
    """利用可能なデータセット一覧を返す（実データのみ）"""
    try:
        datasets = dataset_service.list_datasets()
        return jsonify({
            'success': True,
            'datasets': datasets
        })
    except Exception as e:
        return error_response(str(e), 500)


@datasets_bp.route('/api/datasets/download', methods=['POST'])
def download_dataset_api():
    """データセットをダウンロード/生成"""
    is_valid, error_msg, data = validate_json_request(request, ['name'])
    if not is_valid:
        return error_response(error_msg or 'Invalid request', 400)
    
    name = data.get('name')
    if not name:
        return error_response('dataset name is required', 400)
    
    try:
        success, error_msg, base_path = download_service.start_download(name)
        if not success:
            return error_response(error_msg or 'Failed to start download', 500)
        
        # データセット情報を取得
        info = None
        if name in dataset_service.real_downloader.datasets:
            info = dataset_service.real_downloader.datasets.get(name, {})
        elif name in dataset_service.downloader.datasets:
            info = dataset_service.downloader.datasets.get(name, {})
        
        return jsonify({
            'success': True,
            'started': True,
            'target': base_path,
            'size': info.get('size') if info else None
        })
    except Exception as e:
        return error_response(str(e), 500)


@datasets_bp.route('/api/datasets/status/<dataset_id>', methods=['GET'])
def get_dataset_status(dataset_id: str):
    """現在のダウンロード状態を返す（実データのみ）"""
    try:
        def file_checker(ds_id: str) -> bool:
            base_path = dataset_service.real_downloader.get_dataset_path(ds_id)
            return bool(base_path) and has_any_images(str(base_path))
        
        state = download_service.get_download_status(
            dataset_id,
            check_files=True,
            file_checker=file_checker
        )
        
        if state:
            return jsonify({'success': True, 'status': state})
        else:
            return error_response('Dataset not found', 404)
    except Exception as e:
        return error_response(str(e), 500)


@datasets_bp.route('/api/datasets/details/<dataset_id>', methods=['GET'])
def get_dataset_details(dataset_id: str):
    """データセットの詳細情報を取得"""
    try:
        details = dataset_service.get_dataset_details(dataset_id)
        if details:
            return jsonify({'success': True, 'data': details})
        else:
            return error_response('Dataset not found', 404)
    except Exception as e:
        return error_response(str(e), 500)


@datasets_bp.route('/api/datasets/samples/<dataset_id>', methods=['GET'])
def get_dataset_samples(dataset_id: str):
    """データセットのサンプル画像を取得（JPEG/PNG/BMP/DICOM/NIfTI対応・再帰探索）"""
    try:
        samples = dataset_service.get_dataset_samples(dataset_id)
        
        if not samples:
            return error_response(
                'No images found for this dataset. Please verify dataset path and formats (jpg/png/bmp/tiff/dcm/nii). Upload files using the 📤 button or download the dataset first.',
                404
            )
        
        return jsonify({'success': True, 'samples': samples})
    except Exception as e:
        return error_response(str(e), 500)


@datasets_bp.route('/api/datasets/files/<dataset_id>', methods=['GET'])
def list_dataset_files(dataset_id: str):
    """画像/ラベルのファイル一覧を返す"""
    try:
        kind = request.args.get('kind', 'images')
        limit = int(request.args.get('limit', '50'))
        offset = int(request.args.get('offset', '0'))
        query = (request.args.get('q') or '').lower().strip()
        
        result = dataset_service.list_dataset_files(
            dataset_id,
            kind=kind,
            limit=limit,
            offset=offset,
            query=query
        )
        
        return jsonify({
            'success': True,
            **result
        })
    except Exception as e:
        return error_response(str(e), 500)


@datasets_bp.route('/api/datasets/ingest/<dataset_id>', methods=['POST'])
def ingest_file(dataset_id: str):
    """単一ファイルを指定データセットに取り込む"""
    try:
        is_valid, error_msg, file = validate_file_upload()
        if not is_valid:
            return error_response(error_msg or 'Invalid file upload', 400)
        
        dest = dataset_service.ingest_file(dataset_id, file, file.filename)
        if dest:
            return jsonify({'success': True, 'saved_to': dest})
        else:
            return error_response('Unknown dataset', 404)
    except Exception as e:
        return error_response(str(e), 500)


@datasets_bp.route('/api/datasets/debug-keys')
def debug_dataset_keys():
    """現在ロードされている実データセットID一覧（デバッグ用）"""
    try:
        keys = list(dataset_service.real_downloader.datasets.keys())
        return jsonify({'success': True, 'keys': keys})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

