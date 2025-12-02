"""
CLIコマンドの登録
"""

from typing import Dict, Callable
from src.cli.commands.train_command import TrainCommand
from src.cli.commands.eval_command import EvalCommand
from src.cli.commands.demo_command import DemoCommand
from src.cli.commands.compare_command import CompareCommand
from src.cli.commands.dataset_command import DatasetCommand

# コマンドの登録
COMMANDS: Dict[str, Callable] = {
    'train': TrainCommand.execute,
    'eval': EvalCommand.execute,
    'demo': DemoCommand.execute,
    'compare': CompareCommand.execute,
    'dataset': DatasetCommand.execute,
}


def register_commands() -> Dict[str, Callable]:
    """登録されたコマンドを返す"""
    return COMMANDS


def get_command(command_name: str):
    """コマンドを取得"""
    from typing import Optional
    return COMMANDS.get(command_name)

