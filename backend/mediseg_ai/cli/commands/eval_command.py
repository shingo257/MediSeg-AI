"""
評価コマンド
"""

import os
from typing import Dict, Any, Callable, Optional
from mediseg_ai.cli.base import BaseCommand
from mediseg_ai.utils.common import LoggerManager, DependencyChecker, PathManager
from mediseg_ai.utils.exceptions import ValidationError

logger = LoggerManager.get_logger(__name__)


class EvalCommand(BaseCommand):
    """評価コマンドクラス。runner に evaluate_model を注入して main から登録する。"""

    def __init__(self, runner: Optional[Callable[..., Any]] = None):
        super().__init__()
        self._runner = runner

    def execute(
        self,
        model_path: str,
        data_dir: str,
        save_dir: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """評価を実行。runner が未設定の場合は ValidationError。"""
        if self._runner is None:
            raise ValidationError("EvalCommand requires a runner (evaluate_model) to be set")
        return self._runner(model_path, data_dir, save_dir)

    def validate_inputs(
        self,
        model_path: str,
        data_dir: str,
        save_dir: str,
        **kwargs: Any,
    ) -> bool:
        if not os.path.exists(model_path):
            self.logger.error(f"Model file {model_path} does not exist")
            return False
        if not os.path.exists(data_dir):
            self.logger.error(f"Data directory {data_dir} does not exist")
            return False
        required = ["torch", "torchvision", "numpy", "opencv-python", "matplotlib", "seaborn", "Pillow"]
        if not DependencyChecker.ensure_packages(required, verbose=False):
            self.logger.error("Required packages are not available")
            return False
        PathManager.ensure_directory(save_dir)
        return True

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--model-path",
            type=str,
            default="results/best_model.pth",
            help="Path to trained model checkpoint",
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
