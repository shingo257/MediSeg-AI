"""
モデル選択コンポーネント
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QGroupBox
from PyQt5.QtCore import pyqtSignal


class ModelSelector(QWidget):
    """モデル選択コンポーネント"""
    
    model_selected = pyqtSignal(str)  # モデルが選択されたときに発火
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model_combo = QComboBox()
        self.load_model_btn = QPushButton("🔄 Load Model")
        self.init_ui()
    
    def init_ui(self):
        """UIの初期化"""
        layout = QVBoxLayout(self)
        
        model_group = QGroupBox("Model Selection")
        model_layout = QVBoxLayout(model_group)
        
        self.model_combo.addItems(["U-Net", "DeepLabV3+"])
        model_layout.addWidget(QLabel("Model Type:"))
        model_layout.addWidget(self.model_combo)
        
        self.load_model_btn.clicked.connect(self._on_load_model)
        model_layout.addWidget(self.load_model_btn)
        
        layout.addWidget(model_group)
    
    def _on_load_model(self):
        """モデル読み込みボタンのハンドラ"""
        model_type = self.model_combo.currentText()
        self.model_selected.emit(model_type)
    
    def get_selected_model(self) -> str:
        """選択されたモデル名を取得"""
        return self.model_combo.currentText()
    
    def set_models(self, models: list):
        """利用可能なモデルを設定"""
        self.model_combo.clear()
        self.model_combo.addItems(models)

