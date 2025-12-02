"""
メトリクス表示コンポーネント
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from typing import Dict, Any


class MetricsDisplay(QWidget):
    """メトリクス表示コンポーネント"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.metrics_text = QTextEdit()
        self.init_ui()
    
    def init_ui(self):
        """UIの初期化"""
        layout = QVBoxLayout(self)
        
        self.metrics_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                border-radius: 5px;
                color: white;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.metrics_text)
    
    def display_metrics(self, results: Dict[str, Any]):
        """
        メトリクスを表示
        
        Args:
            results: 結果辞書（metrics, model_typeを含む）
        """
        metrics = results.get('metrics', {})
        model_type = results.get('model_type', 'Unknown')
        
        metrics_text = f"""
Model: {model_type}
========================================

Segmentation Metrics:
• Dice Coefficient: {metrics.get('dice', 0):.4f}
• IoU (Intersection over Union): {metrics.get('iou', 0):.4f}
• Pixel Accuracy: {metrics.get('accuracy', 0):.4f}
• Sensitivity: {metrics.get('sensitivity', 0):.4f}
• Specificity: {metrics.get('specificity', 0):.4f}

Performance Analysis:
• True Positives: {metrics.get('tp', 0)}
• True Negatives: {metrics.get('tn', 0)}
• False Positives: {metrics.get('fp', 0)}
• False Negatives: {metrics.get('fn', 0)}
        """
        
        self.metrics_text.setPlainText(metrics_text)
    
    def clear(self):
        """表示をクリア"""
        self.metrics_text.clear()

