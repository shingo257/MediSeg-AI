"""
共通ユーティリティモジュール
設定管理、ロギング、依存関係チェックなどの共通機能を提供
"""

import os
import sys
import subprocess
import logging
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path
from dataclasses import dataclass, field
import yaml


@dataclass
class AppConfig:
    """アプリケーション設定クラス"""
    # パス設定
    data_dir: str = "data"
    results_dir: str = "results"
    configs_dir: str = "configs"
    
    # モデル設定
    default_model: str = "unet"
    device: str = "auto"  # auto, cpu, cuda
    
    # ログ設定
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # 並列処理設定
    num_workers: int = 4
    batch_size: int = 16
    
    # 環境設定
    debug: bool = False
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """環境変数から設定を読み込む"""
        return cls(
            data_dir=os.environ.get('MEDISEG_DATA_DIR', 'data'),
            results_dir=os.environ.get('MEDISEG_RESULTS_DIR', 'results'),
            configs_dir=os.environ.get('MEDISEG_CONFIGS_DIR', 'configs'),
            default_model=os.environ.get('MEDISEG_DEFAULT_MODEL', 'unet'),
            device=os.environ.get('MEDISEG_DEVICE', 'auto'),
            log_level=os.environ.get('MEDISEG_LOG_LEVEL', 'INFO'),
            log_file=os.environ.get('MEDISEG_LOG_FILE'),
            num_workers=int(os.environ.get('MEDISEG_NUM_WORKERS', '4')),
            batch_size=int(os.environ.get('MEDISEG_BATCH_SIZE', '16')),
            debug=os.environ.get('MEDISEG_DEBUG', 'false').lower() == 'true',
        )
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        """設定値の検証"""
        # パス存在確認
        for path_name, path_value in [
            ("data_dir", self.data_dir),
            ("results_dir", self.results_dir),
            ("configs_dir", self.configs_dir),
        ]:
            path = Path(path_value)
            if not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    return False, f"Failed to create {path_name}: {e}"
        
        # ログレベル検証
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_levels:
            return False, f"Invalid log level: {self.log_level}"
        
        # 数値範囲検証
        if self.batch_size <= 0:
            return False, "Batch size must be positive"
        
        if self.num_workers < 0:
            return False, "Number of workers must be non-negative"
        
        return True, None


class ConfigLoader:
    """設定ファイルローダー"""
    
    @staticmethod
    def load_yaml(config_path: str) -> Dict[str, Any]:
        """YAMLファイルから設定を読み込む"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config or {}
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format in {config_path}: {e}")
    
    @staticmethod
    def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
        """複数の設定を再帰的にマージ"""
        result = {}
        for config in configs:
            if config is None:
                continue
            for key, value in config.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = ConfigLoader.merge_configs(result[key], value)
                else:
                    result[key] = value
        return result

    @staticmethod
    def ensure_config(config_path: str, default_template: Dict[str, Any]) -> Dict[str, Any]:
        """設定ファイルが存在しなければ default_template を YAML で書き出してから読み込んで返す。"""
        path = Path(config_path)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_template, f, default_flow_style=False, allow_unicode=True)
        return ConfigLoader.load_yaml(config_path)


class DependencyChecker:
    """依存関係チェッカー"""
    
    @staticmethod
    def check_packages(packages: List[str]) -> List[str]:
        """パッケージの存在確認"""
        missing = []
        for package in packages:
            try:
                module_name = package.replace('-', '_')
                __import__(module_name)
            except ImportError:
                missing.append(package)
        return missing
    
    @staticmethod
    def install_packages(packages: List[str], verbose: bool = True) -> bool:
        """パッケージをインストール"""
        for package in packages:
            try:
                if verbose:
                    print(f"Installing {package}...")
                subprocess.check_call(
                    [sys.executable, '-m', 'pip', 'install', package],
                    stdout=None if verbose else subprocess.DEVNULL,
                    stderr=None if verbose else subprocess.DEVNULL
                )
                if verbose:
                    print(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                return False
        return True
    
    @staticmethod
    def ensure_packages(packages: List[str], verbose: bool = True) -> bool:
        """パッケージをチェックして不足があればインストール"""
        missing = DependencyChecker.check_packages(packages)
        if not missing:
            return True
        
        if verbose:
            print(f"❌ Missing packages: {', '.join(missing)}")
        
        return DependencyChecker.install_packages(missing, verbose=verbose)


class LoggerManager:
    """ロギング管理クラス"""
    
    @staticmethod
    def setup_logger(name: Optional[str] = None, level: str = "INFO") -> logging.Logger:
        """ロガーをセットアップ"""
        logger = logging.getLogger(name)
        
        # 既存のハンドラーをクリアして重複を防ぐ
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, level.upper()))
        logger.propagate = False
        
        return logger
    
    @staticmethod
    def get_logger(name: Optional[str] = None) -> logging.Logger:
        """既存のロガーを取得"""
        return logging.getLogger(name)


class PathManager:
    """パス管理ユーティリティ"""
    
    @staticmethod
    def get_project_root() -> Path:
        """プロジェクトルートディレクトリを取得"""
        return Path(__file__).resolve().parent.parent.parent

    @staticmethod
    def ensure_directory(path: str) -> Path:
        """ディレクトリを存在確認して作成"""
        path_obj = Path(path)
        path_obj.mkdir(parents=True, exist_ok=True)
        return path_obj

    @staticmethod
    def get_data_paths() -> Dict[str, Path]:
        """主要なデータディレクトリのパスを取得"""
        root = PathManager.get_project_root()
        return {
            "project_root": root,
            "data": root / "data",
            "results": root / "results",
            "configs": root / "configs",
            "templates": root / "templates",
            "static": root / "static",
            "notebooks": root / "notebooks",
        }


# グローバルインスタンス
app_config = AppConfig.from_env()