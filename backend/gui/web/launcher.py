"""
Web GUI起動ロジック統合モジュール
モデルセットアップ、システム監視、Flaskアプリ起動を統合管理
"""

import logging
import webbrowser
import time
import threading
from typing import Optional

from backend.gui.web.config import WebGUIConfig
from backend.gui.web.web_gui import app
from backend.gui.web.services import setup_models
from mediseg_ai.utils.system_monitor import system_monitor
from mediseg_ai.utils.exceptions import ModelLoadError

logger = logging.getLogger(__name__)


class WebGUILauncher:
    """Web GUI起動クラス"""
    
    def __init__(self, config: Optional[WebGUIConfig] = None):
        """
        初期化
        
        Args:
            config: Web GUI設定。Noneの場合は環境変数から読み込む
        """
        self.config = config or WebGUIConfig.from_env()
        self._monitoring_started = False
        self._models_setup = False
        
        # 設定の検証
        is_valid, error_msg = self.config.validate()
        if not is_valid:
            raise ValueError(f"Invalid configuration: {error_msg}")
    
    def setup_models(self) -> bool:
        """
        モデルのセットアップ
        
        Returns:
            セットアップが成功したかどうか
        """
        try:
            if setup_models():
                self._models_setup = True
                return True
            else:
                logger.error("Failed to setup models")
                return False
        except ModelLoadError:
            raise
        except Exception as e:
            logger.exception("Unexpected error in setup_models")
            print(f"[ERROR] Failed to setup models: {e}")
            return False
    
    def start_monitoring(self) -> bool:
        """
        システム監視の開始
        
        Returns:
            監視の開始が成功したかどうか
        """
        try:
            system_monitor.start_monitoring()
            self._monitoring_started = True
            print("[INFO] System monitoring started")
            return True
        except Exception as e:
            logger.warning("System monitoring failed to start: %s", e)
            print(f"[WARN] System monitoring failed to start: {e}")
            return False
    
    def _open_browser(self):
        """ブラウザを開く（内部メソッド）"""
        try:
            time.sleep(self.config.browser_delay)
            webbrowser.open(self.config.get_url())
        except Exception as e:
            logger.warning("Failed to open browser: %s", e)
            print(f"[WARN] Failed to open browser: {e}")
            print(f"Please manually open: {self.config.get_url()}")
    
    def launch(self) -> None:
        """
        Web GUIを起動
        
        モデルセットアップ、システム監視、Flaskアプリ起動を順次実行
        """
        print("Starting MediSeg.AI Web GUI...")
        print(f"Open your browser and go to: {self.config.get_url()}")
        
        # モデルのセットアップ
        if not self.setup_models():
            raise RuntimeError("Failed to setup models")
        
        # システム監視を開始
        self.start_monitoring()
        
        # ブラウザを自動で開く
        if self.config.auto_open_browser:
            print(f"Opening browser in {self.config.browser_delay} seconds...")
            browser_thread = threading.Thread(target=self._open_browser)
            browser_thread.daemon = True
            browser_thread.start()
        
        # Flaskアプリを起動
        try:
            app.run(
                debug=self.config.debug,
                host=self.config.host,
                port=self.config.port
            )
        finally:
            # クリーンアップ処理
            self.cleanup()
    
    def cleanup(self) -> None:
        """
        クリーンアップ処理
        
        システム監視の停止など、終了時の処理を実行
        """
        if self._monitoring_started:
            try:
                system_monitor.stop_monitoring()
                print("[INFO] System monitoring stopped")
            except Exception as e:
                logger.warning("System monitoring stop error: %s", e)
                print(f"[WARN] System monitoring stop error: {e}")

