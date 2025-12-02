"""
アプリケーション状態管理クラス
グローバル変数の代替として使用
"""

from typing import Optional, Dict, Any
import numpy as np
import torch.nn as nn


class AppState:
    """アプリケーション状態の管理クラス"""
    
    def __init__(self):
        self.models: Dict[str, nn.Module] = {}
        self.current_image: Optional[np.ndarray] = None
        self.current_results: Optional[Dict[str, Any]] = None
        self.build_info: Dict[str, str] = {
            'app': 'MediSeg.AI',
            'version': 'web_gui.samples-real-only',
        }
    
    def set_model(self, name: str, model: nn.Module) -> None:
        """モデルを設定"""
        self.models[name] = model
    
    def get_model(self, name: str) -> Optional[nn.Module]:
        """モデルを取得"""
        return self.models.get(name)
    
    def has_model(self, name: str) -> bool:
        """モデルが存在するかチェック"""
        return name in self.models
    
    def set_current_image(self, image: np.ndarray) -> None:
        """現在の画像を設定"""
        self.current_image = image.copy() if image is not None else None
    
    def get_current_image(self) -> Optional[np.ndarray]:
        """現在の画像を取得"""
        return self.current_image
    
    def set_current_results(self, results: Dict[str, Any]) -> None:
        """現在の結果を設定"""
        self.current_results = results
    
    def get_current_results(self) -> Optional[Dict[str, Any]]:
        """現在の結果を取得"""
        return self.current_results
    
    def clear_results(self) -> None:
        """結果をクリア"""
        self.current_results = None
    
    def clear_image(self) -> None:
        """画像をクリア"""
        self.current_image = None
    
    def clear_all(self) -> None:
        """すべての状態をクリア"""
        self.clear_image()
        self.clear_results()


# グローバルインスタンス（後方互換性のため）
_app_state = AppState()

def get_app_state() -> AppState:
    """アプリケーション状態のシングルトンインスタンスを取得"""
    return _app_state

