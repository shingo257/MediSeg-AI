"""
評価コマンド
"""

import os
from typing import Dict, Any
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EvalCommand:
    """評価コマンドクラス"""
    
    @staticmethod
    def execute(model_path: str, data_dir: str, save_dir: str) -> Dict[str, Any]:
        """
        評価を実行
        
        Args:
            model_path: モデルファイルのパス
            data_dir: データディレクトリ
            save_dir: 保存ディレクトリ
            
        Returns:
            評価結果
        """
        from main import evaluate_model
        
        if not os.path.exists(model_path):
            logger.error(f"Model file {model_path} does not exist")
            logger.info("Please train a model first")
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        logger.info("Starting evaluation...")
        results = evaluate_model(model_path, data_dir, save_dir)
        logger.info("Evaluation completed!")
        
        return results

