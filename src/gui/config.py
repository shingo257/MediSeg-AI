"""
Web GUI設定管理モジュール
環境変数からの設定読み込みとデフォルト値の管理
"""

import os
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class WebGUIConfig:
    """Web GUI起動設定クラス"""
    host: str = '127.0.0.1'
    port: int = 8080
    debug: bool = False
    auto_open_browser: bool = True
    browser_delay: float = 3.0
    max_content_length: int = 16 * 1024 * 1024  # 16MB
    data_dir: str = 'data'
    upload_dir: str = 'uploads'
    
    @classmethod
    def from_env(cls) -> 'WebGUIConfig':
        """環境変数から設定を読み込む"""
        return cls(
            host=os.environ.get('MEDISEG_HOST', '127.0.0.1'),
            port=int(os.environ.get('MEDISEG_PORT', '8080')),
            debug=os.environ.get('MEDISEG_DEBUG', 'false').lower() == 'true',
            auto_open_browser=os.environ.get('MEDISEG_AUTO_OPEN_BROWSER', 'true').lower() == 'true',
            browser_delay=float(os.environ.get('MEDISEG_BROWSER_DELAY', '3.0')),
            max_content_length=int(os.environ.get('MEDISEG_MAX_CONTENT_LENGTH', str(16 * 1024 * 1024))),
            data_dir=os.environ.get('DATA_DIR', 'data'),
            upload_dir=os.environ.get('MEDISEG_UPLOAD_DIR', 'uploads')
        )
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        """設定値の検証"""
        if not isinstance(self.port, int) or self.port < 1 or self.port > 65535:
            return False, f"Invalid port number: {self.port}. Must be between 1 and 65535"
        
        if not isinstance(self.browser_delay, (int, float)) or self.browser_delay < 0:
            return False, f"Invalid browser delay: {self.browser_delay}. Must be >= 0"
        
        if not isinstance(self.host, str) or not self.host:
            return False, f"Invalid host: {self.host}. Must be a non-empty string"
        
        if not isinstance(self.max_content_length, int) or self.max_content_length < 0:
            return False, f"Invalid max content length: {self.max_content_length}. Must be >= 0"
        
        return True, None
    
    def get_url(self) -> str:
        """Web GUIのURLを取得"""
        return f"http://{self.host}:{self.port}"

