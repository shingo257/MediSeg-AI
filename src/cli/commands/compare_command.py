"""
モデル比較コマンド
"""

import os
from typing import Dict, Any
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CompareCommand:
    """モデル比較コマンドクラス"""
    
    @staticmethod
    def execute(dataset: str, data_dir: str, save_dir: str) -> Dict[str, Any]:
        """
        モデル比較を実行
        
        Args:
            dataset: データセット名
            data_dir: データディレクトリ
            save_dir: 保存ディレクトリ
            
        Returns:
            比較結果
        """
        if not os.path.exists(data_dir):
            logger.error(f"Data directory {data_dir} does not exist")
            logger.info("Please download dataset first")
            raise FileNotFoundError(f"Data directory not found: {data_dir}")
        
        from src.training.compare_models import main as compare_main
        import sys
        
        logger.info(f"Starting model comparison on {dataset}...")
        sys.argv = [
            'compare_models.py',
            '--dataset', dataset,
            '--data_dir', data_dir,
            '--save_dir', save_dir
        ]
        compare_main()
        logger.info("Model comparison completed!")
        
        return {}

