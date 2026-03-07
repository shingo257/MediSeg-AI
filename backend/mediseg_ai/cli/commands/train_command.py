"""
訓練コマンド（train / train-medical 共通）
"""

import os
from typing import Any, Callable, Optional
from mediseg_ai.cli.base import BaseCommand
from mediseg_ai.utils.common import LoggerManager
from mediseg_ai.utils.exceptions import ValidationError

logger = LoggerManager.get_logger(__name__)


class TrainCommand(BaseCommand):
    """訓練コマンドクラス。runner に train_model を注入して main から登録する。"""

    def __init__(self, runner: Optional[Callable[..., Any]] = None):
        super().__init__()
        self._runner = runner

    def execute(
        self,
        config_path: str,
        data_dir: str,
        save_dir: str,
        **kwargs: Any,
    ) -> Any:
        """訓練を実行。runner が未設定の場合は ValidationError。"""
        if self._runner is None:
            raise ValidationError("TrainCommand requires a runner (train_model) to be set")
        return self._runner(config_path, data_dir, save_dir)

    def validate_inputs(
        self,
        config_path: str,
        data_dir: str,
        save_dir: str,
        **kwargs: Any,
    ) -> bool:
        if not os.path.exists(data_dir):
            self.logger.error(f"Data directory {data_dir} does not exist")
            return False
        return True

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--config",
            type=str,
            default="configs/base_config.yaml",
            help="Config path",
        )
        parser.add_argument(
            "--data-dir",
            type=str,
            default="data/pascal_voc",
            help="Dataset directory",
        )
        parser.add_argument(
            "--save-dir",
            type=str,
            default="results",
            help="Output directory",
        )
