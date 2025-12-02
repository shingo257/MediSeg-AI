"""
デモコマンド
"""

from src.utils.logger import get_logger

logger = get_logger(__name__)


class DemoCommand:
    """デモコマンドクラス"""
    
    @staticmethod
    def execute() -> None:
        """デモを実行"""
        from main import demo_model
        
        logger.info("Starting demo...")
        demo_model()
        logger.info("Demo completed!")

