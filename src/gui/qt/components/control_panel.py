"""
コントロールパネルコンポーネント
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QGroupBox, QSlider, QProgressBar, QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal


class ControlPanel(QWidget):
    """コントロールパネルコンポーネント"""
    
    load_image_requested = pyqtSignal()
    save_results_requested = pyqtSignal()
    run_inference_requested = pyqtSignal(float)  # 閾値を送信
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.load_btn = QPushButton("📁 Load Image")
        self.save_btn = QPushButton("💾 Save Results")
        self.inference_btn = QPushButton("🚀 Run Inference")
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_label = QLabel("0.50")
        self.progress_bar = QProgressBar()
        self.log_text = QTextEdit()
        self.init_ui()
    
    def init_ui(self):
        """UIの初期化"""
        layout = QVBoxLayout(self)
        
        # タイトル
        title = QLabel("MediSeg.AI")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #0078d4;
                padding: 10px;
                text-align: center;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # ファイル操作
        file_group = QGroupBox("File Operations")
        file_layout = QVBoxLayout(file_group)
        
        self.load_btn.clicked.connect(self.load_image_requested.emit)
        file_layout.addWidget(self.load_btn)
        
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_results_requested.emit)
        file_layout.addWidget(self.save_btn)
        
        layout.addWidget(file_group)
        
        # 推論設定
        inference_group = QGroupBox("Inference Settings")
        inference_layout = QVBoxLayout(inference_group)
        
        # 閾値スライダー
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Threshold:"))
        self.threshold_slider.setRange(0, 100)
        self.threshold_slider.setValue(50)
        self.threshold_slider.valueChanged.connect(self._update_threshold)
        threshold_layout.addWidget(self.threshold_slider)
        threshold_layout.addWidget(self.threshold_label)
        inference_layout.addLayout(threshold_layout)
        
        self.inference_btn.setEnabled(False)
        self.inference_btn.clicked.connect(self._on_run_inference)
        inference_layout.addWidget(self.inference_btn)
        
        layout.addWidget(inference_group)
        
        # プログレスバー
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # ログ表示
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                border-radius: 5px;
                color: #00ff00;
                font-family: 'Courier New', monospace;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        # スペーサー
        layout.addStretch()
    
    def _update_threshold(self, value: int):
        """閾値スライダーの更新"""
        threshold = value / 100.0
        self.threshold_label.setText(f"{threshold:.2f}")
    
    def _on_run_inference(self):
        """推論ボタンのハンドラ"""
        threshold = self.threshold_slider.value() / 100.0
        self.run_inference_requested.emit(threshold)
    
    def get_threshold(self) -> float:
        """現在の閾値を取得"""
        return self.threshold_slider.value() / 100.0
    
    def set_inference_enabled(self, enabled: bool):
        """推論ボタンの有効/無効を設定"""
        self.inference_btn.setEnabled(enabled)
    
    def set_save_enabled(self, enabled: bool):
        """保存ボタンの有効/無効を設定"""
        self.save_btn.setEnabled(enabled)
    
    def show_progress(self, value: int):
        """プログレスバーを表示"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(value)
    
    def hide_progress(self):
        """プログレスバーを非表示"""
        self.progress_bar.setVisible(False)
    
    def log(self, message: str):
        """ログにメッセージを追加"""
        self.log_text.append(message)

