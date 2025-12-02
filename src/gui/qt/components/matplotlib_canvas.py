"""
カスタムMatplotlibキャンバス
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from typing import Dict, Any


class MatplotlibCanvas(FigureCanvas):
    """カスタムMatplotlibキャンバス"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#2b2b2b')
        super().__init__(self.fig)
        self.setParent(parent)
        
        # ダークテーマの設定
        plt.style.use('dark_background')
        self.fig.patch.set_facecolor('#2b2b2b')
        
    def plot_segmentation(self, original: np.ndarray, prediction: np.ndarray, mask: np.ndarray, metrics: Dict[str, Any]):
        """セグメンテーション結果をプロット"""
        self.fig.clear()
        
        # 3つのサブプロットを作成
        ax1 = self.fig.add_subplot(131)
        ax2 = self.fig.add_subplot(132)
        ax3 = self.fig.add_subplot(133)
        
        # 元画像
        ax1.imshow(original)
        ax1.set_title('Original Image', color='white', fontsize=12, fontweight='bold')
        ax1.axis('off')
        
        # 予測結果
        im2 = ax2.imshow(prediction, cmap='viridis')
        ax2.set_title('Prediction Heatmap', color='white', fontsize=12, fontweight='bold')
        ax2.axis('off')
        self.fig.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)
        
        # バイナリマスク
        ax3.imshow(mask, cmap='gray')
        ax3.set_title('Binary Mask', color='white', fontsize=12, fontweight='bold')
        ax3.axis('off')
        
        # メトリクスをテキストで表示
        metrics_text = f"Dice: {metrics.get('dice', 0):.3f}\nIoU: {metrics.get('iou', 0):.3f}\nAccuracy: {metrics.get('accuracy', 0):.3f}"
        self.fig.text(0.02, 0.02, metrics_text, fontsize=10, color='white', 
                     bbox=dict(boxstyle="round,pad=0.3", facecolor='#404040', alpha=0.8))
        
        self.draw()

