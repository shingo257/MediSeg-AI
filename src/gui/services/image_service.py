"""
画像サービス
画像処理と可視化
"""

import io
import base64
import numpy as np
import cv2
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional

from src.gui.state.app_state import get_app_state


class ImageService:
    """画像処理と可視化のサービス"""
    
    def __init__(self):
        self.app_state = get_app_state()
    
    def create_visualization(
        self, 
        image: np.ndarray, 
        prediction: np.ndarray, 
        mask: np.ndarray, 
        metrics: Dict[str, Any]
    ) -> str:
        """
        可視化の作成
        
        Args:
            image: 元画像
            prediction: 予測結果
            mask: バイナリマスク
            metrics: メトリクス
            
        Returns:
            Base64エンコードされた可視化画像
        """
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.patch.set_facecolor('#2b2b2b')
        
        # 元画像
        axes[0, 0].imshow(image)
        axes[0, 0].set_title('Original Image', color='white', fontsize=14, fontweight='bold')
        axes[0, 0].axis('off')
        
        # 予測ヒートマップ
        im1 = axes[0, 1].imshow(prediction, cmap='viridis')
        axes[0, 1].set_title('Prediction Heatmap', color='white', fontsize=14, fontweight='bold')
        axes[0, 1].axis('off')
        plt.colorbar(im1, ax=axes[0, 1], fraction=0.046, pad=0.04)
        
        # バイナリマスク
        axes[1, 0].imshow(mask, cmap='gray')
        axes[1, 0].set_title('Binary Mask', color='white', fontsize=14, fontweight='bold')
        axes[1, 0].axis('off')
        
        # オーバーレイ
        overlay = image.copy()
        overlay[mask > 0] = [255, 0, 0]  # 赤色でオーバーレイ
        axes[1, 1].imshow(overlay)
        axes[1, 1].set_title('Overlay', color='white', fontsize=14, fontweight='bold')
        axes[1, 1].axis('off')
        
        # メトリクスをテキストで表示
        metrics_text = f"""
Model: {metrics.get('model_type', 'Unknown')}
Dice: {metrics.get('dice', 0):.3f}
IoU: {metrics.get('iou', 0):.3f}
Accuracy: {metrics.get('accuracy', 0):.3f}
Sensitivity: {metrics.get('sensitivity', 0):.3f}
Specificity: {metrics.get('specificity', 0):.3f}
        """
        
        fig.text(0.02, 0.02, metrics_text, fontsize=10, color='white', 
                 bbox=dict(boxstyle="round,pad=0.3", facecolor='#404040', alpha=0.8))
        
        # 画像をBase64エンコード
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                    facecolor='#2b2b2b', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    def generate_mask_image(self) -> Optional[str]:
        """マスク画像を生成"""
        results = self.app_state.get_current_results()
        image = self.app_state.get_current_image()
        
        if results is None or image is None:
            return None
        
        mask = results.get('binary_mask')
        if mask is None:
            return None
        
        # マスクを画像としてエンコード
        fig, ax = plt.subplots(1, 1, figsize=(8, 8))
        fig.patch.set_facecolor('#2b2b2b')
        ax.imshow(mask, cmap='gray')
        ax.set_title('Binary Mask', color='white', fontsize=14, fontweight='bold')
        ax.axis('off')
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                    facecolor='#2b2b2b', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    def generate_contour_image(self) -> Optional[str]:
        """輪郭画像を生成"""
        results = self.app_state.get_current_results()
        image = self.app_state.get_current_image()
        
        if results is None or image is None:
            return None
        
        mask = results.get('binary_mask')
        if mask is None:
            return None
        
        # 輪郭を検出
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 輪郭を描画
        contour_image = image.copy()
        cv2.drawContours(contour_image, contours, -1, (0, 255, 0), 2)
        
        # 画像をエンコード
        fig, ax = plt.subplots(1, 1, figsize=(8, 8))
        fig.patch.set_facecolor('#2b2b2b')
        ax.imshow(contour_image)
        ax.set_title('Contour', color='white', fontsize=14, fontweight='bold')
        ax.axis('off')
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                    facecolor='#2b2b2b', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    def encode_image_to_base64(self, image: np.ndarray) -> str:
        """
        画像をBase64エンコード
        
        Args:
            image: RGB画像（numpy配列）
            
        Returns:
            Base64エンコードされた画像文字列
        """
        _, buffer = cv2.imencode('.jpg', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        return base64.b64encode(buffer).decode()

