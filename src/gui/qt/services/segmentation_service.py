"""
セグメンテーション処理サービス
"""

import torch
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from typing import Dict, Any, Optional
import torch.nn as nn

from src.utils.logger import get_logger

logger = get_logger(__name__)


class SegmentationWorker(QThread):
    """モデル推論用のワーカースレッド"""
    progress = pyqtSignal(int)
    result = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, model: nn.Module, image: np.ndarray, model_type: str, threshold: float = 0.5):
        super().__init__()
        self.model = model
        self.image = image
        self.model_type = model_type
        self.threshold = threshold
    
    def run(self):
        """推論を実行"""
        try:
            self.progress.emit(10)
            
            # 画像の前処理
            if len(self.image.shape) == 3:
                image_tensor = torch.from_numpy(self.image).permute(2, 0, 1).float() / 255.0
            else:
                image_tensor = torch.from_numpy(self.image).float() / 255.0
            
            image_tensor = image_tensor.unsqueeze(0)  # バッチ次元を追加
            
            self.progress.emit(30)
            
            # モデル推論
            self.model.eval()
            with torch.no_grad():
                prediction = self.model(image_tensor)
            
            self.progress.emit(70)
            
            # 結果の後処理
            prediction = torch.sigmoid(prediction).squeeze().cpu().numpy()
            binary_mask = (prediction > self.threshold).astype(np.uint8)
            
            self.progress.emit(90)
            
            # メトリクス計算（ターゲットがない場合はメトリクスを計算しない）
            results = {}
            
            self.progress.emit(100)
            
            self.result.emit({
                'prediction': prediction,
                'binary_mask': binary_mask,
                'metrics': results,
                'model_type': self.model_type
            })
            
        except Exception as e:
            logger.error(f"Segmentation error: {e}")
            self.error.emit(str(e))


class SegmentationService:
    """セグメンテーション処理のサービス"""
    
    def __init__(self, model_manager):
        """
        初期化
        
        Args:
            model_manager: ModelManagerインスタンス
        """
        self.model_manager = model_manager
        self.current_worker: Optional[SegmentationWorker] = None
    
    def create_worker(
        self, 
        model_type: str, 
        image: np.ndarray, 
        threshold: float = 0.5
    ) -> Optional[SegmentationWorker]:
        """
        セグメンテーションワーカーを作成
        
        Args:
            model_type: モデルタイプ名
            image: 入力画像
            threshold: 閾値
            
        Returns:
            ワーカー、モデルが存在しない場合はNone
        """
        model = self.model_manager.get_model(model_type)
        if model is None:
            logger.error(f"Model {model_type} not available")
            return None
        
        return SegmentationWorker(model, image, model_type, threshold)
    
    def cancel_current_worker(self):
        """現在のワーカーをキャンセル"""
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.terminate()
            self.current_worker.wait()
            self.current_worker = None

