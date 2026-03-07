"""
モデル比較コマンド
"""

import os
from typing import Any, Callable, Optional
from mediseg_ai.cli.base import BaseCommand
from mediseg_ai.utils.common import LoggerManager
from mediseg_ai.utils.exceptions import ValidationError

logger = LoggerManager.get_logger(__name__)


class CompareCommand(BaseCommand):
    """比較コマンドクラス。compare_models.run を引数で呼ぶ。"""

    def __init__(self, runner: Optional[Callable[..., Any]] = None):
        super().__init__()
        self._runner = runner

    def execute(
        self,
        dataset: str,
        data_dir: str,
        save_dir: str,
        **kwargs: Any,
    ) -> Any:
        """比較を実行。runner (compare_models.run) に引数を渡して実行。"""
        if self._runner is None:
            raise ValidationError("CompareCommand requires a runner (compare_models.run) to be set")
        batch_size = kwargs.get("batch_size", 8)
        return self._runner(
            dataset=dataset,
            data_dir=data_dir,
            save_dir=save_dir,
            batch_size=batch_size,
        )

    def validate_inputs(
        self,
        dataset: str,
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
            "--dataset",
            type=str,
            choices=["pascal_voc", "isic"],
            default="pascal_voc",
            help="Dataset to use",
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
        parser.add_argument(
            "--batch-size",
            type=int,
            default=8,
            help="Batch size for evaluation",
        )
