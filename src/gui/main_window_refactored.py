"""
MediSeg.AI - メインGUIウィンドウ（リファクタリング版）
新しいコンポーネントとサービスを使用
"""

import sys
import os
import numpy as np
import cv2
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QFileDialog, QTabWidget, QSplitter, 
    QStatusBar, QMessageBox
)
from PyQt5.QtCore import Qt

# プロジェクトのパスを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.gui.qt.components.control_panel import ControlPanel
from src.gui.qt.components.image_viewer import ImageViewer
from src.gui.qt.components.metrics_display import MetricsDisplay
from src.gui.qt.components.model_selector import ModelSelector
from src.gui.qt.services.model_manager import ModelManager
from src.gui.qt.services.segmentation_service import SegmentationService
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MediSegGUI(QMainWindow):
    """MediSeg.AI メインGUIウィンドウ（リファクタリング版）"""
    
    def __init__(self):
        super().__init__()
        self.current_image: np.ndarray = None
        self.current_results = None
        
        # サービス層の初期化
        self.model_manager = ModelManager()
        self.segmentation_service = SegmentationService(self.model_manager)
        
        # UIコンポーネントの初期化
        self.control_panel = None
        self.image_viewer = None
        self.metrics_display = None
        self.model_selector = None
        
        self.init_ui()
        self._connect_signals()
    
    def init_ui(self):
        """UIの初期化"""
        self.setWindowTitle("MediSeg.AI - Medical Image Segmentation")
        self.setGeometry(100, 100, 1400, 900)
        
        # ダークテーマの設定
        self._apply_dark_theme()
        
        # メインウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # メインレイアウト
        main_layout = QHBoxLayout(central_widget)
        
        # 左パネル（コントロール）
        self.control_panel = ControlPanel()
        self.model_selector = ModelSelector()
        
        # コントロールパネルとモデルセレクターを統合
        left_panel_widget = QWidget()
        left_layout = QVBoxLayout(left_panel_widget)
        left_layout.addWidget(self.control_panel)
        left_layout.addWidget(self.model_selector)
        left_layout.addStretch()
        
        # 左パネルとして使用
        left_panel = left_panel_widget
        
        # 右パネル（結果表示）
        right_panel = self._create_result_panel()
        
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
    
    def _apply_dark_theme(self):
        """ダークテーマの適用"""
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
    
    def _create_result_panel(self):
        """結果表示パネルの作成"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # タブウィジェット
        tab_widget = QTabWidget()
        
        # セグメンテーション結果タブ
        self.image_viewer = ImageViewer()
        tab_widget.addTab(self.image_viewer, "🎯 Segmentation")
        
        # メトリクスタブ
        self.metrics_display = MetricsDisplay()
        tab_widget.addTab(self.metrics_display, "📊 Metrics")
        
        layout.addWidget(tab_widget)
        
        return panel
    
    def _connect_signals(self):
        """シグナルとスロットの接続"""
        # コントロールパネルのシグナル
        self.control_panel.load_image_requested.connect(self._load_image)
        self.control_panel.save_results_requested.connect(self._save_results)
        self.control_panel.run_inference_requested.connect(self._run_inference)
        
        # モデルセレクターのシグナル
        self.model_selector.model_selected.connect(self._on_model_selected)
    
    def _load_image(self):
        """画像の読み込み"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Image", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        
        if file_path:
            try:
                self.current_image = cv2.imread(file_path)
                if self.current_image is not None:
                    self.current_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
                    self.control_panel.log(f"✅ Image loaded: {os.path.basename(file_path)}")
                    self.control_panel.log(f"   Size: {self.current_image.shape}")
                    self.control_panel.set_inference_enabled(True)
                    self.control_panel.set_save_enabled(True)
                else:
                    self.control_panel.log("❌ Failed to load image")
            except Exception as e:
                self.control_panel.log(f"❌ Error loading image: {str(e)}")
                logger.error(f"Error loading image: {e}")
    
    def _on_model_selected(self, model_type: str):
        """モデルが選択されたときのハンドラ"""
        if self.model_manager.has_model(model_type):
            self.control_panel.log(f"✅ {model_type} model selected")
        else:
            self.control_panel.log(f"❌ Model {model_type} not available")
    
    def _run_inference(self, threshold: float):
        """推論の実行"""
        if self.current_image is None:
            self.control_panel.log("❌ Please load an image first")
            return
        
        model_type = self.model_selector.get_selected_model()
        if not self.model_manager.has_model(model_type):
            self.control_panel.log("❌ Please select a model first")
            return
        
        # 既存のワーカーをキャンセル
        self.segmentation_service.cancel_current_worker()
        
        # 新しいワーカーを作成
        worker = self.segmentation_service.create_worker(
            model_type, 
            self.current_image, 
            threshold
        )
        
        if worker is None:
            self.control_panel.log("❌ Failed to create worker")
            return
        
        self.segmentation_service.current_worker = worker
        
        # シグナルの接続
        worker.progress.connect(self.control_panel.show_progress)
        worker.result.connect(self._display_results)
        worker.error.connect(self._handle_error)
        
        # ワーカーの開始
        worker.start()
        
        self.control_panel.log(f"🚀 Running inference with {model_type}...")
    
    def _display_results(self, results):
        """結果の表示"""
        self.control_panel.hide_progress()
        self.current_results = results
        
        # セグメンテーション結果の表示
        self.image_viewer.plot_segmentation(
            self.current_image,
            results['prediction'],
            results['binary_mask'],
            results['metrics']
        )
        
        # メトリクスの表示
        self.metrics_display.display_metrics(results)
        
        self.control_panel.log("✅ Inference completed successfully!")
        if 'metrics' in results and 'dice' in results['metrics']:
            self.control_panel.log(f"   Dice: {results['metrics']['dice']:.4f}")
            self.control_panel.log(f"   IoU: {results['metrics']['iou']:.4f}")
    
    def _handle_error(self, error_msg: str):
        """エラーの処理"""
        self.control_panel.hide_progress()
        self.control_panel.log(f"❌ Error: {error_msg}")
        QMessageBox.critical(self, "Error", f"Inference failed:\n{error_msg}")
        logger.error(f"Inference error: {error_msg}")
    
    def _save_results(self):
        """結果の保存"""
        if self.current_results is None:
            self.control_panel.log("❌ No results to save")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "", 
            "PNG Files (*.png);;JPEG Files (*.jpg)"
        )
        
        if file_path:
            try:
                self.image_viewer.canvas.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                self.control_panel.log(f"✅ Results saved: {os.path.basename(file_path)}")
            except Exception as e:
                self.control_panel.log(f"❌ Error saving results: {str(e)}")
                logger.error(f"Error saving results: {e}")
    
    def closeEvent(self, event):
        """アプリケーション終了時の処理"""
        # 実行中のワーカーをキャンセル
        self.segmentation_service.cancel_current_worker()
        
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

