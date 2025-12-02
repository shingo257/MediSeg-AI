"""
統一されたロギング設定
"""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str = 'mediseg',
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    ロガーをセットアップ
    
    Args:
        name: ロガー名
        level: ログレベル
        format_string: フォーマット文字列（Noneの場合はデフォルト）
        
    Returns:
        設定済みロガー
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 既存のハンドラをクリア
    logger.handlers.clear()
    
    # フォーマット
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    
    # コンソールハンドラ
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# デフォルトロガー
default_logger = setup_logger()


def get_logger(name: str = 'mediseg') -> logging.Logger:
    """
    ロガーを取得（既存のロガーを返すか、新規作成）
    
    Args:
        name: ロガー名
        
    Returns:
        ロガー
    """
    return logging.getLogger(name)

