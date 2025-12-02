"""
モデル管理サービス
"""

from typing import Dict, Optional
import torch.nn as nn

from src.models.unet import UNet
from src.models.deeplabv3plus import create_deeplabv3plus
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ModelManager:
    """モデル管理サービス"""
    
    def __init__(self):
        self.models: Dict[str, nn.Module] = {}
        self._setup_models()
    
    def _setup_models(self):
        """モデルのセットアップ"""
        logger.info("Setting up models...")
        
        # U-Netモデル
        try:
            self.models['U-Net'] = UNet(n_channels=3, n_classes=1, bilinear=False)
            logger.info("✅ U-Net model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load U-Net: {e}")
        
        # DeepLabV3+モデル
        try:
            self.models['DeepLabV3+'] = create_deeplabv3plus(
                num_classes=1, 
                backbone='resnet50', 
                pretrained=False
            )
            logger.info("✅ DeepLabV3+ model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load DeepLabV3+: {e}")
        
        logger.info("Model setup completed!")
    
    def get_model(self, model_type: str) -> Optional[nn.Module]:
        """
        モデルを取得
        
        Args:
            model_type: モデルタイプ名
            
        Returns:
            モデル、存在しない場合はNone
        """
        return self.models.get(model_type)
    
    def has_model(self, model_type: str) -> bool:
        """
        モデルが存在するかチェック
        
        Args:
            model_type: モデルタイプ名
            
        Returns:
            モデルが存在する場合True
        """
        return model_type in self.models
    
    def get_available_models(self) -> list:
        """利用可能なモデルのリストを取得"""
        return list(self.models.keys())

