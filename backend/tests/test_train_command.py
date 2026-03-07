"""Test TrainCommand execute with mocked runner."""
import pytest
from unittest.mock import patch
from mediseg_ai.cli.commands.train_command import TrainCommand
from mediseg_ai.utils.exceptions import ValidationError


@patch("mediseg_ai.cli.commands.train_command.os.path.exists", return_value=True)
def test_train_command_execute_calls_runner(mock_exists):
    """TrainCommand().execute(...) calls the injected runner with config_path, data_dir, save_dir."""
    calls = []

    def fake_runner(config_path: str, data_dir: str, save_dir: str):
        calls.append((config_path, data_dir, save_dir))
        return {"best_dice": 0.9, "final_epoch": 10}

    cmd = TrainCommand(runner=fake_runner)
    result = cmd.execute(
        config_path="/tmp/config.yaml",
        data_dir="/tmp/data",
        save_dir="/tmp/out",
    )
    assert len(calls) == 1
    assert calls[0] == ("/tmp/config.yaml", "/tmp/data", "/tmp/out")
    assert result["best_dice"] == 0.9
    assert result["final_epoch"] == 10


def test_train_command_execute_raises_without_runner():
    """TrainCommand without runner raises ValidationError on execute."""
    cmd = TrainCommand(runner=None)
    with pytest.raises(ValidationError, match="runner"):
        cmd.execute(
            config_path="/tmp/config.yaml",
            data_dir="/tmp/data",
            save_dir="/tmp/out",
        )
