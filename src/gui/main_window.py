"""
MediSeg.AI - メインGUIウィンドウ
カッコイイビジュアルの医療画像セグメンテーションGUI
"""

import sys
import os
import torch
import numpy as np
import cv2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                            QFileDialog, QProgressBar, QTextEdit, QTabWidget,
                            QSlider, QSpinBox, QComboBox, QGroupBox, QFrame,
                            QSplitter, QScrollArea, QMessageBox, QStatusBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette, QColor, QIcon, QPainter, QPen
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns

# プロジェクトのパスを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.unet import UNet
from models.deeplabv3plus import create_deeplabv3plus
from evaluation.metrics import SegmentationMetrics


class ModelWorker(QThread):
    """モデル推論用のワーカースレッド"""
    progress = pyqtSignal(int)
    result = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, model, image, model_type):
        super().__init__()
        self.model = model
        self.image = image
        self.model_type = model_type
    
    def run(self):
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
            binary_mask = (prediction > 0.5).astype(np.uint8)
            
            self.progress.emit(90)
            
            # メトリクス計算（ターゲットがない場合はメトリクスを計算しない）
            # 実際のセグメンテーション結果のみを返す
            results = {}
            # 注: メトリクス計算にはターゲット（正解）マスクが必要です
            
            self.progress.emit(100)
            
            self.result.emit({
                'prediction': prediction,
                'binary_mask': binary_mask,
                'metrics': results,
                'model_type': self.model_type
            })
            
        except Exception as e:
            self.error.emit(str(e))


class MatplotlibCanvas(FigureCanvas):
    """カスタムMatplotlibキャンバス"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#2b2b2b')
        super().__init__(self.fig)
        self.setParent(parent)
        
        # ダークテーマの設定
        plt.style.use('dark_background')
        self.fig.patch.set_facecolor('#2b2b2b')
        
    def plot_segmentation(self, original, prediction, mask, metrics):
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
        metrics_text = f"Dice: {metrics['dice']:.3f}\nIoU: {metrics['iou']:.3f}\nAccuracy: {metrics['accuracy']:.3f}"
        self.fig.text(0.02, 0.02, metrics_text, fontsize=10, color='white', 
                     bbox=dict(boxstyle="round,pad=0.3", facecolor='#404040', alpha=0.8))
        
        self.draw()


class MediSegGUI(QMainWindow):
    """MediSeg.AI メインGUIウィンドウ"""
    
    def __init__(self):
        super().__init__()
        self.current_image = None
        self.current_model = None
        self.current_model_type = None
        self.init_ui()
        self.setup_models()
        
    def init_ui(self):
        """UIの初期化"""
        self.setWindowTitle("MediSeg.AI - Medical Image Segmentation")
        self.setGeometry(100, 100, 1400, 900)
        
        # ダークテーマの設定
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: white;
            }
            QWidget {
                background-color: #2b2b2b;
                color: white;
            }
            QPushButton {
                background-color: #404040;
                border: 2px solid #555555;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background-color: #505050;
                border-color: #0078d4;
            }
            QPushButton:pressed {
                background-color: #0078d4;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #404040;
                border: 1px solid #555555;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
            }
            QProgressBar {
                border: 2px solid #555555;
                border-radius: 5px;
                text-align: center;
                background-color: #404040;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """)
        
        # メインウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # メインレイアウト
        main_layout = QHBoxLayout(central_widget)
        
        # 左パネル（コントロール）
        left_panel = self.create_control_panel()
        
        # 右パネル（結果表示）
        right_panel = self.create_result_panel()
        
        # スプリッターで分割
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 1000])
        
        main_layout.addWidget(splitter)
        
        # ステータスバー
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - MediSeg.AI")
        
    def create_control_panel(self):
        """コントロールパネルの作成"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
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
        
        self.load_btn = QPushButton("📁 Load Image")
        self.load_btn.clicked.connect(self.load_image)
        file_layout.addWidget(self.load_btn)
        
        self.save_btn = QPushButton("💾 Save Results")
        self.save_btn.clicked.connect(self.save_results)
        self.save_btn.setEnabled(False)
        file_layout.addWidget(self.save_btn)
        
        layout.addWidget(file_group)
        
        # モデル選択
        model_group = QGroupBox("Model Selection")
        model_layout = QVBoxLayout(model_group)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["U-Net", "DeepLabV3+"])
        model_layout.addWidget(QLabel("Model Type:"))
        model_layout.addWidget(self.model_combo)
        
        self.load_model_btn = QPushButton("🔄 Load Model")
        self.load_model_btn.clicked.connect(self.load_model)
        model_layout.addWidget(self.load_model_btn)
        
        layout.addWidget(model_group)
        
        # 推論設定
        inference_group = QGroupBox("Inference Settings")
        inference_layout = QVBoxLayout(inference_group)
        
        # 閾値スライダー
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Threshold:"))
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(0, 100)
        self.threshold_slider.setValue(50)
        self.threshold_slider.valueChanged.connect(self.update_threshold)
        threshold_layout.addWidget(self.threshold_slider)
        self.threshold_label = QLabel("0.50")
        threshold_layout.addWidget(self.threshold_label)
        inference_layout.addLayout(threshold_layout)
        
        # 推論ボタン
        self.inference_btn = QPushButton("🚀 Run Inference")
        self.inference_btn.clicked.connect(self.run_inference)
        self.inference_btn.setEnabled(False)
        inference_layout.addWidget(self.inference_btn)
        
        layout.addWidget(inference_group)
        
        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # ログ表示
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
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
        
        return panel
    
    def create_result_panel(self):
        """結果表示パネルの作成"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        
        # セグメンテーション結果タブ
        self.segmentation_tab = QWidget()
        seg_layout = QVBoxLayout(self.segmentation_tab)
        
        self.canvas = MatplotlibCanvas(self, width=10, height=6)
        seg_layout.addWidget(self.canvas)
        
        self.tab_widget.addTab(self.segmentation_tab, "🎯 Segmentation")
        
        # メトリクスタブ
        self.metrics_tab = QWidget()
        metrics_layout = QVBoxLayout(self.metrics_tab)
        
        self.metrics_text = QTextEdit()
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
        metrics_layout.addWidget(self.metrics_text)
        
        self.tab_widget.addTab(self.metrics_tab, "📊 Metrics")
        
        layout.addWidget(self.tab_widget)
        
        return panel
    
    def setup_models(self):
        """モデルのセットアップ"""
        self.models = {}
        self.log("Setting up models...")
        
        # U-Netモデル
        try:
            self.models['U-Net'] = UNet(n_channels=3, n_classes=1, bilinear=False)
            self.log("✅ U-Net model loaded successfully")
        except Exception as e:
            self.log(f"❌ Failed to load U-Net: {str(e)}")
        
        # DeepLabV3+モデル
        try:
            self.models['DeepLabV3+'] = create_deeplabv3plus(num_classes=1, backbone='resnet50', pretrained=False)
            self.log("✅ DeepLabV3+ model loaded successfully")
        except Exception as e:
            self.log(f"❌ Failed to load DeepLabV3+: {str(e)}")
        
        self.log("Model setup completed!")
    
    def load_image(self):
        """画像の読み込み"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Image", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        
        if file_path:
            try:
                # 画像の読み込み
                self.current_image = cv2.imread(file_path)
                if self.current_image is not None:
                    self.current_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
                    self.log(f"✅ Image loaded: {os.path.basename(file_path)}")
                    self.log(f"   Size: {self.current_image.shape}")
                    self.inference_btn.setEnabled(True)
                    self.save_btn.setEnabled(True)
                else:
                    self.log("❌ Failed to load image")
            except Exception as e:
                self.log(f"❌ Error loading image: {str(e)}")
    
    def load_model(self):
        """モデルの読み込み"""
        model_type = self.model_combo.currentText()
        if model_type in self.models:
            self.current_model = self.models[model_type]
            self.current_model_type = model_type
            self.log(f"✅ {model_type} model selected")
        else:
            self.log(f"❌ Model {model_type} not available")
    
    def run_inference(self):
        """推論の実行"""
        if self.current_image is None:
            self.log("❌ Please load an image first")
            return
        
        if self.current_model is None:
            self.log("❌ Please select a model first")
            return
        
        # プログレスバーを表示
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # ワーカースレッドで推論実行
        self.worker = ModelWorker(self.current_model, self.current_image, self.current_model_type)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.result.connect(self.display_results)
        self.worker.error.connect(self.handle_error)
        self.worker.start()
        
        self.log(f"🚀 Running inference with {self.current_model_type}...")
    
    def display_results(self, results):
        """結果の表示"""
        self.progress_bar.setVisible(False)
        
        # セグメンテーション結果の表示
        self.canvas.plot_segmentation(
            self.current_image,
            results['prediction'],
            results['binary_mask'],
            results['metrics']
        )
        
        # メトリクスの表示
        metrics_text = f"""
Model: {results['model_type']}
========================================

Segmentation Metrics:
• Dice Coefficient: {results['metrics']['dice']:.4f}
• IoU (Intersection over Union): {results['metrics']['iou']:.4f}
• Pixel Accuracy: {results['metrics']['accuracy']:.4f}
• Sensitivity: {results['metrics']['sensitivity']:.4f}
• Specificity: {results['metrics']['specificity']:.4f}

Performance Analysis:
• Prediction Quality: {'Excellent' if results['metrics']['dice'] > 0.8 else 'Good' if results['metrics']['dice'] > 0.6 else 'Fair' if results['metrics']['dice'] > 0.4 else 'Poor'}
• Segmentation Confidence: {results['metrics']['dice']*100:.1f}%

Model Information:
• Model Type: {results['model_type']}
• Input Shape: {self.current_image.shape}
• Output Shape: {results['prediction'].shape}
        """
        
        self.metrics_text.setText(metrics_text)
        
        # タブを結果に切り替え
        self.tab_widget.setCurrentIndex(0)
        
        self.log("✅ Inference completed successfully!")
        self.log(f"   Dice: {results['metrics']['dice']:.4f}")
        self.log(f"   IoU: {results['metrics']['iou']:.4f}")
    
    def handle_error(self, error_msg):
        """エラーの処理"""
        self.progress_bar.setVisible(False)
        self.log(f"❌ Error: {error_msg}")
        QMessageBox.critical(self, "Error", f"Inference failed:\n{error_msg}")
    
    def update_threshold(self, value):
        """閾値の更新"""
        threshold = value / 100.0
        self.threshold_label.setText(f"{threshold:.2f}")
    
    def save_results(self):
        """結果の保存"""
        if not hasattr(self, 'current_results'):
            self.log("❌ No results to save")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "", 
            "PNG Files (*.png);;JPEG Files (*.jpg)"
        )
        
        if file_path:
            try:
                # 結果画像の保存
                self.canvas.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                self.log(f"✅ Results saved: {os.path.basename(file_path)}")
            except Exception as e:
                self.log(f"❌ Error saving results: {str(e)}")
    
    def log(self, message):
        """ログメッセージの追加"""
        self.log_text.append(f"[{QTimer().remainingTime()}] {message}")
        self.log_text.ensureCursorVisible()
    
    def closeEvent(self, event):
        """アプリケーション終了時の処理"""
        reply = QMessageBox.question(
            self, 'Exit', 'Are you sure you want to exit?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    """メイン関数"""
    app = QApplication(sys.argv)
    
    # アプリケーションの設定
    app.setApplicationName("MediSeg.AI")
    app.setApplicationVersion("1.0.0")
    
    # メインウィンドウの作成と表示
    window = MediSegGUI()
    window.show()
    
    # アプリケーションの実行
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
