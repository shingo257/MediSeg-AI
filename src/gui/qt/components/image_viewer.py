"""
画像表示コンポーネント
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from src.gui.qt.components.matplotlib_canvas import MatplotlibCanvas


class ImageViewer(QWidget):
    """画像表示コンポーネント"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = MatplotlibCanvas(self, width=10, height=6)
        self.init_ui()
    
    def init_ui(self):
        """UIの初期化"""
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
    
    def plot_segmentation(self, original, prediction, mask, metrics):
        """セグメンテーション結果をプロット"""
        self.canvas.plot_segmentation(original, prediction, mask, metrics)
    
    def clear(self):
        """表示をクリア"""
        self.canvas.fig.clear()
        self.canvas.draw()

