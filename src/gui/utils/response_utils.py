"""
レスポンス生成ユーティリティ
"""

from flask import jsonify
from typing import Any, Dict, Optional, Tuple


def success_response(data: Any = None, message: Optional[str] = None) -> Tuple[Dict[str, Any], int]:
    """
    成功レスポンスを生成
    
    Args:
        data: レスポンスデータ
        message: オプショナルメッセージ
        
    Returns:
        (JSONレスポンス, HTTPステータスコード)
    """
    response = {'success': True}
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    return jsonify(response), 200


def error_response(
    error: str, 
    status_code: int = 500, 
    additional_data: Optional[Dict[str, Any]] = None
) -> Tuple[Dict[str, Any], int]:
    """
    エラーレスポンスを生成
    
    Args:
        error: エラーメッセージ
        status_code: HTTPステータスコード
        additional_data: 追加データ
        
    Returns:
        (JSONレスポンス, HTTPステータスコード)
    """
    response = {'success': False, 'error': error}
    if additional_data:
        response.update(additional_data)
    return jsonify(response), status_code


def validate_json_request(request, required_fields: list) -> Tuple[bool, Optional[str], Optional[Dict]]:
    """
    JSONリクエストを検証
    
    Args:
        request: Flaskリクエストオブジェクト
        required_fields: 必須フィールドのリスト
        
    Returns:
        (検証成功, エラーメッセージ, データ)
    """
    try:
        data = request.get_json(force=True)
        if not data:
            return False, 'No JSON data provided', None
        
        for field in required_fields:
            if field not in data:
                return False, f'Missing required field: {field}', None
        
        return True, None, data
    except Exception as e:
        return False, f'Invalid JSON: {str(e)}', None

