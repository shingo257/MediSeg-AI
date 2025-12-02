"""
入力検証ユーティリティ
"""

from flask import request
from werkzeug.utils import secure_filename
from typing import Tuple, Optional
import os

from src.gui.utils.image_utils import EXTENSIONS


def validate_file_upload() -> Tuple[bool, Optional[str], Optional[object]]:
    """
    ファイルアップロードを検証
    
    Returns:
        (検証成功, エラーメッセージ, ファイルオブジェクト)
    """
    if 'file' not in request.files:
        return False, 'No file uploaded', None
    
    file = request.files['file']
    if file.filename == '':
        return False, 'No file selected', None
    
    return True, None, file


def validate_image_file(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    画像ファイルを検証
    
    Args:
        file_path: ファイルパス
        
    Returns:
        (検証成功, エラーメッセージ)
    """
    if not os.path.exists(file_path):
        return False, 'File does not exist'
    
    filename = os.path.basename(file_path)
    if not filename.lower().endswith(EXTENSIONS):
        return False, f'Invalid file type. Supported: {", ".join(EXTENSIONS)}'
    
    return True, None


def validate_dataset_id(dataset_id: str, available_datasets: dict) -> Tuple[bool, Optional[str]]:
    """
    データセットIDを検証
    
    Args:
        dataset_id: データセットID
        available_datasets: 利用可能なデータセットの辞書
        
    Returns:
        (検証成功, エラーメッセージ)
    """
    if not dataset_id:
        return False, 'Dataset ID is required'
    
    if dataset_id not in available_datasets:
        return False, f'Unknown dataset: {dataset_id}'
    
    return True, None

