"""Test EvalCommand execute with mocked runner."""
import pytest
from unittest.mock import patch, MagicMock
from mediseg_ai.cli.commands.eval_command import EvalCommand
from mediseg_ai.utils.exceptions import ValidationError


@patch("mediseg_ai.cli.commands.eval_command.DependencyChecker.ensure_packages", return_value=True)
@patch("mediseg_ai.cli.commands.eval_command.PathManager.ensure_directory")
@patch("mediseg_ai.cli.commands.eval_command.os.path.exists", return_value=True)
def test_eval_command_execute_calls_runner(mock_ensure_packages, mock_ensure_dir, mock_exists):
    """EvalCommand().execute(...) calls the injected runner with model_path, data_dir, save_dir."""
    calls = []

    def fake_runner(model_path: str, data_dir: str, save_dir: str):
        calls.append((model_path, data_dir, save_dir))
        return {"iou": 0.9, "dice": 0.85}

    cmd = EvalCommand(runner=fake_runner)
    result = cmd.execute(
        model_path="/tmp/model.pth",
        data_dir="/tmp/data",
        save_dir="/tmp/out",
    )
    assert len(calls) == 1
    assert calls[0] == ("/tmp/model.pth", "/tmp/data", "/tmp/out")
    assert result["iou"] == 0.9
    assert result["dice"] == 0.85


def test_eval_command_execute_raises_without_runner():
    """EvalCommand without runner raises ValidationError on execute."""
    cmd = EvalCommand(runner=None)
    with pytest.raises(ValidationError, match="runner"):
        cmd.execute(
            model_path="/tmp/model.pth",
            data_dir="/tmp/data",
            save_dir="/tmp/out",
        )
