"""
エラーハンドリングの統一ユーティリティ
"""

import traceback
from typing import Optional, Dict, Any
from flask import jsonify

from src.utils.errors import MediSegError


def handle_error(error: Exception, include_traceback: bool = False) -> tuple:
    """
    エラーを処理してJSONレスポンスを生成
    
    Args:
        error: 例外オブジェクト
        include_traceback: トレースバックを含めるか（デバッグ用）
        
    Returns:
        (JSONレスポンス, HTTPステータスコード)
    """
    if isinstance(error, MediSegError):
        status_code = 400
        error_message = str(error)
    else:
        status_code = 500
        error_message = "Internal server error"
    
    response = {
        'success': False,
        'error': error_message
    }
    
    if include_traceback:
        response['traceback'] = traceback.format_exc()
    
    return jsonify(response), status_code


def create_error_response(
    message: str,
    status_code: int = 500,
    additional_data: Optional[Dict[str, Any]] = None
) -> tuple:
    """
    エラーレスポンスを生成
    
    Args:
        message: エラーメッセージ
        status_code: HTTPステータスコード
        additional_data: 追加データ
        
    Returns:
        (JSONレスポンス, HTTPステータスコード)
    """
    response = {
        'success': False,
        'error': message
    }
    
    if additional_data:
        response.update(additional_data)
    
    return jsonify(response), status_code

