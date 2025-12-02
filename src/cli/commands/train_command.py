"""
訓練コマンド
"""

import os
from typing import Dict, Any
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TrainCommand:
    """訓練コマンドクラス"""
    
    @staticmethod
    def execute(config_path: str, data_dir: str, save_dir: str) -> Dict[str, Any]:
        """
        訓練を実行
        
        Args:
            config_path: 設定ファイルのパス
            data_dir: データディレクトリ
            save_dir: 保存ディレクトリ
            
        Returns:
            訓練結果のサマリー
        """
        from main import train_model
        
        if not os.path.exists(data_dir):
            logger.error(f"Data directory {data_dir} does not exist")
            logger.info("Please download Pascal VOC 2012 dataset first")
            raise FileNotFoundError(f"Data directory not found: {data_dir}")
        
        logger.info("Starting training...")
        summary = train_model(config_path, data_dir, save_dir)
        logger.info("Training completed!")
        
        return summary

