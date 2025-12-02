"""
モデルサービス
モデルの管理と推論処理
"""

import torch
import torch.nn as nn
from typing import Dict, Optional, Tuple
import numpy as np

from src.models.unet import UNet
from src.models.deeplabv3plus import create_deeplabv3plus
from src.gui.state.app_state import get_app_state


class ModelService:
    """モデル管理と推論処理のサービス"""
    
    def __init__(self):
        self.app_state = get_app_state()
    
    def setup_models(self) -> bool:
        """
        モデルのセットアップ
        
        Returns:
            セットアップが成功したかどうか
        """
        try:
            self.app_state.set_model('U-Net', UNet(n_channels=3, n_classes=1, bilinear=False))
            self.app_state.set_model(
                'DeepLabV3+', 
                create_deeplabv3plus(num_classes=1, backbone='resnet50', pretrained=False)
            )
            print("✅ Models loaded successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to load models: {e}")
            return False
    
    def get_model(self, model_type: str) -> Optional[nn.Module]:
        """
        モデルを取得
        
        Args:
            model_type: モデルタイプ名
            
        Returns:
            モデル、存在しない場合はNone
        """
        return self.app_state.get_model(model_type)
    
    def has_model(self, model_type: str) -> bool:
        """
        モデルが存在するかチェック
        
        Args:
            model_type: モデルタイプ名
            
        Returns:
            モデルが存在する場合True
        """
        return self.app_state.has_model(model_type)
    
    def get_available_models(self) -> list:
        """
        利用可能なモデルのリストを取得
        
        Returns:
            モデル名のリスト
        """
        return list(self.app_state.models.keys())
    
    def process_image(
        self, 
        image: np.ndarray, 
        model_type: str, 
        threshold: float = 0.5
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        画像の処理とセグメンテーション
        
        Args:
            image: RGB画像（numpy配列）
            model_type: モデルタイプ名
            threshold: 閾値
            
        Returns:
            (結果辞書, エラーメッセージ)
        """
        try:
            # モデルの取得
            model = self.get_model(model_type)
            if model is None:
                return None, f"Model {model_type} not available"
            
            # 画像の前処理
            image_tensor = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0
            image_tensor = image_tensor.unsqueeze(0)  # バッチ次元を追加
            
            # モデル推論
            model.eval()
            with torch.no_grad():
                prediction = model(image_tensor)
            
            # 結果の後処理
            prediction = torch.sigmoid(prediction).squeeze().cpu().numpy()
            binary_mask = (prediction > threshold).astype(np.uint8)
            
            # メトリクス計算（ターゲットがない場合はメトリクスを計算しない）
            results = {}
            
            result_dict = {
                'prediction': prediction,
                'binary_mask': binary_mask,
                'metrics': results,
                'model_type': model_type,
                'threshold': threshold
            }
            
            # 状態に保存
            self.app_state.set_current_image(image)
            self.app_state.set_current_results(result_dict)
            
            return result_dict, None
            
        except Exception as e:
            return None, str(e)

