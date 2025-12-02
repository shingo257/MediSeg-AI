"""
データセット関連コマンド
"""

from src.utils.logger import get_logger

logger = get_logger(__name__)


class DatasetCommand:
    """データセットコマンドクラス"""
    
    @staticmethod
    def execute(mode: str = 'auto') -> None:
        """
        データセット関連のコマンドを実行
        
        Args:
            mode: モード ('auto' or 'real')
        """
        if mode == 'auto':
            logger.info("🚀 Auto Dataset Demo...")
            try:
                from src.data_loaders.auto_dataset import demo_auto_dataset
                demo_auto_dataset()
            except ImportError as e:
                logger.error(f"Failed to import auto dataset: {e}")
            except Exception as e:
                logger.error(f"Auto dataset demo failed: {e}")
        elif mode == 'real':
            logger.info("🌍 Real Datasets Demo...")
            try:
                from src.data_loaders.real_datasets import main as real_datasets_main
                real_datasets_main()
            except ImportError as e:
                logger.error(f"Failed to import real datasets: {e}")
            except Exception as e:
                logger.error(f"Real datasets demo failed: {e}")
        else:
            logger.error(f"Unknown dataset mode: {mode}")

