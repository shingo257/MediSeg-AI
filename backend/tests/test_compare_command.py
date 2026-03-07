"""Test CompareCommand execute with mocked runner."""
import pytest
from unittest.mock import patch
from mediseg_ai.cli.commands.compare_command import CompareCommand
from mediseg_ai.utils.exceptions import ValidationError


@patch("mediseg_ai.cli.commands.compare_command.os.path.exists", return_value=True)
def test_compare_command_execute_calls_runner(mock_exists):
    """CompareCommand().execute(...) calls the injected runner with dataset, data_dir, save_dir, batch_size."""
    calls = []

    def fake_run(dataset: str, data_dir: str, save_dir: str, batch_size: int = 8):
        calls.append((dataset, data_dir, save_dir, batch_size))
        return None

    cmd = CompareCommand(runner=fake_run)
    cmd.execute(
        dataset="pascal_voc",
        data_dir="/tmp/data",
        save_dir="/tmp/out",
    )
    assert len(calls) == 1
    assert calls[0] == ("pascal_voc", "/tmp/data", "/tmp/out", 8)


@patch("mediseg_ai.cli.commands.compare_command.os.path.exists", return_value=True)
def test_compare_command_execute_passes_batch_size(mock_exists):
    """CompareCommand().execute(...) passes batch_size from kwargs to runner."""
    calls = []

    def fake_run(dataset: str, data_dir: str, save_dir: str, batch_size: int = 8):
        calls.append((dataset, data_dir, save_dir, batch_size))
        return None

    cmd = CompareCommand(runner=fake_run)
    cmd.execute(
        dataset="isic",
        data_dir="/tmp/data",
        save_dir="/tmp/out",
        batch_size=16,
    )
    assert len(calls) == 1
    assert calls[0][3] == 16


def test_compare_command_execute_raises_without_runner():
    """CompareCommand without runner raises ValidationError on execute."""
    cmd = CompareCommand(runner=None)
    with pytest.raises(ValidationError, match="runner"):
        cmd.execute(
            dataset="pascal_voc",
            data_dir="/tmp/data",
            save_dir="/tmp/out",
        )
