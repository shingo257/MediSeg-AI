"""Verify that main modules and CLI/Web GUI can be imported."""
import pytest


def test_import_mediseg_ai():
    import mediseg_ai
    assert mediseg_ai is not None


def test_import_mediseg_ai_utils_exceptions():
    from mediseg_ai.utils.exceptions import ValidationError, ModelLoadError, DatasetError
    assert ValidationError is not None
    assert ModelLoadError is not None
    assert DatasetError is not None


def test_import_cli_base():
    from mediseg_ai.cli.base import BaseCommand, CommandRegistry, command_registry
    assert BaseCommand is not None
    assert command_registry is not None


def test_import_cli_commands():
    from mediseg_ai.cli.commands.eval_command import EvalCommand
    from mediseg_ai.cli.commands.train_command import TrainCommand
    from mediseg_ai.cli.commands.compare_command import CompareCommand
    assert EvalCommand is not None
    assert TrainCommand is not None
    assert CompareCommand is not None


def test_import_backend_gui_web_launcher():
    from backend.gui.web.launcher import WebGUILauncher
    from backend.gui.web.config import WebGUIConfig
    assert WebGUILauncher is not None
    assert WebGUIConfig is not None


def test_import_common_config_loader():
    from mediseg_ai.utils.common import ConfigLoader, PathManager
    assert ConfigLoader.ensure_config is not None
    assert PathManager.get_project_root is not None
