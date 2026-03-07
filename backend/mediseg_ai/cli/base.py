"""
CLIコマンドの基底クラス
すべてのCLIコマンドで共通の機能を提供
"""

import abc
import argparse
from typing import Dict, Any, Optional
from mediseg_ai.utils.common import LoggerManager
from mediseg_ai.utils.exceptions import ValidationError

logger = LoggerManager.get_logger(__name__)


class BaseCommand(abc.ABC):
    """すべてのCLIコマンドの基底クラス"""

    def __init__(self):
        """初期化"""
        self.logger = LoggerManager.get_logger(self.__class__.__name__)

    @abc.abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """コマンドを実行"""
        pass

    def validate_inputs(self, **kwargs) -> bool:
        """入力値の検証。各コマンドで必要に応じてオーバーライドする。デフォルトではTrueを返す。"""
        return True

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """コマンド固有の引数を追加。各コマンドで必要に応じてオーバーライドする。"""
        pass

    def handle_exception(self, func):
        """例外処理のデコレータ"""
        from functools import wraps

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValidationError as e:
                self.logger.error(f"Validation error: {e}")
                raise
            except Exception as e:
                self.logger.error(f"Unexpected error in {func.__name__}: {e}")
                raise
        return wrapper

    def log_execution(self, **kwargs) -> None:
        """実行開始をログに記録"""
        self.logger.info(f"Executing {self.__class__.__name__} with {kwargs}")

    def log_completion(self, result: Any = None) -> None:
        """実行完了をログに記録"""
        if result:
            self.logger.info(f"Completed {self.__class__.__name__} with result: {result}")
        else:
            self.logger.info(f"Completed {self.__class__.__name__}")


class CommandRegistry:
    """コマンドレジストリ"""

    def __init__(self):
        self.commands: Dict[str, BaseCommand] = {}

    def register(self, name: str, command: BaseCommand) -> None:
        """コマンドを登録"""
        if name in self.commands:
            raise ValueError(f"Command {name} is already registered")
        if not isinstance(command, BaseCommand):
            raise TypeError(f"Command must inherit from BaseCommand, got {type(command)}")
        self.commands[name] = command
        logger.info(f"Registered command: {name}")

    def get(self, name: str) -> BaseCommand:
        """コマンドを取得"""
        return self.commands[name]

    def list_commands(self) -> list:
        """登録済みコマンド一覧を返す"""
        return list(self.commands.keys())

    def execute(self, name: str, **kwargs) -> Any:
        """指定されたコマンドを実行"""
        if name not in self.commands:
            raise KeyError(f"Unknown command: {name}")
        command = self.commands[name]
        command.log_execution(**kwargs)
        try:
            if command.validate_inputs(**kwargs):
                result = command.execute(**kwargs)
                command.log_completion(result)
                return result
            else:
                raise ValidationError(f"Invalid inputs for command {name}")
        except Exception as e:
            logger.error(f"Failed to execute command {name}: {e}")
            raise


# グローバルレジストリ
command_registry = CommandRegistry()
