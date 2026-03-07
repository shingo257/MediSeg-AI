"""
Main execution script for MediSeg.AI project
"""

import os
import sys
import argparse
import torch
from pathlib import Path
from typing import Any, Dict, Optional

from mediseg_ai.models.unet import UNet
from mediseg_ai.config import get_default_isic_config
from mediseg_ai.evaluation.runner import evaluate_model
from mediseg_ai.training.runner import train_model


def demo_model() -> None:
    """Demonstrate model with dummy data."""
    print("=" * 60)
    print("MediSeg.AI - Model Demonstration")
    print("=" * 60)
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create model
    model = UNet(n_channels=3, n_classes=1, bilinear=False).to(device)
    print(f"Model created with {sum(p.numel() for p in model.parameters()):,} parameters")
    
    # Test with dummy data
    print("Testing with dummy data...")
    batch_size = 2
    height, width = 256, 256
    
    # Create dummy input
    dummy_input = torch.randn(batch_size, 3, height, width).to(device)
    
    # Forward pass
    model.eval()
    with torch.no_grad():
        output = model(dummy_input)
    
    print(f"Input shape: {dummy_input.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Output range: [{output.min():.4f}, {output.max():.4f}]")
    
    # Test metrics with more realistic dummy data
    from mediseg_ai.evaluation.metrics import SegmentationMetrics
    
    # より現実的なダミーデータを生成
    # 予測値を0-1の範囲に正規化
    output_normalized = torch.sigmoid(output)
    
    # ターゲットも0-1の範囲で、予測値とある程度重複するように生成
    dummy_target = torch.rand(batch_size, 1, height, width).to(device)
    # ターゲットをバイナリ化（0.5を閾値として）
    dummy_target = (dummy_target > 0.5).float()
    
    metrics = SegmentationMetrics()
    metrics.update(output, dummy_target)
    results = metrics.compute()
    
    print("\nMetrics on dummy data:")
    for metric, value in results.items():
        print(f"{metric.capitalize()}: {value:.4f}")
    
    # より詳細な情報を表示
    print(f"\nDetailed analysis:")
    print(f"Target shape: {dummy_target.shape}")
    print(f"Target unique values: {torch.unique(dummy_target)}")
    print(f"Target positive ratio: {dummy_target.mean():.4f}")
    
    # 予測値の統計
    pred_binary = (torch.sigmoid(output) > 0.5).float()
    print(f"Prediction positive ratio: {pred_binary.mean():.4f}")
    print(f"Overlap ratio: {(pred_binary * dummy_target).sum() / (pred_binary + dummy_target).clamp(max=1).sum():.4f}")
    
    print("Demo completed!")


def main() -> None:
    """Main function (subcommand-based CLI)."""
    from mediseg_ai.cli.base import command_registry
    from mediseg_ai.cli.commands.train_command import TrainCommand
    from mediseg_ai.cli.commands.eval_command import EvalCommand
    from mediseg_ai.cli.commands.compare_command import CompareCommand
    from mediseg_ai.training.compare_models import run as compare_run

    command_registry.register("train", TrainCommand(runner=train_model))
    command_registry.register(
        "train-medical",
        TrainCommand(runner=lambda c, d, s: train_model(c, d, s, get_default_isic_config(), "isic")),
    )
    command_registry.register("eval", EvalCommand(runner=evaluate_model))
    command_registry.register("compare", CompareCommand(runner=compare_run))

    parser = argparse.ArgumentParser(
        description="MediSeg.AI - Medical Image Segmentation"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    train_parser = subparsers.add_parser("train", help="Train on Pascal VOC")
    command_registry.get("train").add_arguments(train_parser)

    train_med_parser = subparsers.add_parser(
        "train-medical", help="Train on a medical dataset (default: ISIC)"
    )
    train_med_parser.add_argument(
        "--config", type=str, default="configs/isic_config.yaml", help="Config path"
    )
    train_med_parser.add_argument(
        "--data-dir", type=str, default="data/medical/isic", help="Dataset directory"
    )
    train_med_parser.add_argument(
        "--save-dir", type=str, default="results", help="Output directory"
    )

    eval_parser = subparsers.add_parser("eval", help="Evaluate a trained model")
    command_registry.get("eval").add_arguments(eval_parser)

    compare_parser = subparsers.add_parser("compare", help="Compare models")
    command_registry.get("compare").add_arguments(compare_parser)

    subparsers.add_parser("demo", help="Run a dummy forward/metrics demo")

    # datasets
    datasets_parser = subparsers.add_parser("datasets", help="Dataset demos")
    datasets_parser.add_argument(
        "kind", choices=["auto", "real"], help="Which dataset demo to run"
    )

    # gui
    gui_parser = subparsers.add_parser("gui", help="Launch GUI")
    gui_parser.add_argument(
        "--type",
        choices=["web", "desktop"],
        default="web",
        help="GUI type to launch",
    )
    gui_parser.add_argument("--host", type=str, default=None, help="Web GUI host")
    gui_parser.add_argument("--port", type=int, default=None, help="Web GUI port")
    gui_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    gui_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not auto-open browser for Web GUI",
    )

    args = parser.parse_args()

    if args.command == "train":
        command_registry.execute(
            "train",
            config_path=args.config,
            data_dir=args.data_dir,
            save_dir=args.save_dir,
        )
        return

    if args.command == "train-medical":
        command_registry.execute(
            "train-medical",
            config_path=args.config,
            data_dir=args.data_dir,
            save_dir=args.save_dir,
        )
        return

    if args.command == "eval":
        command_registry.execute(
            "eval",
            model_path=args.model_path,
            data_dir=args.data_dir,
            save_dir=args.save_dir,
        )
        return

    if args.command == "compare":
        command_registry.execute(
            "compare",
            dataset=args.dataset,
            data_dir=args.data_dir,
            save_dir=args.save_dir,
            batch_size=getattr(args, "batch_size", 8),
        )
        return

    if args.command == "demo":
        demo_model()
        return

    if args.command == "datasets":
        if args.kind == "auto":
            print("🚀 Auto Dataset Demo...")
            from mediseg_ai.data_loaders.auto_dataset import demo_auto_dataset

            demo_auto_dataset()
            return

        print("🌍 Real Datasets Demo...")
        from mediseg_ai.data_loaders.real_datasets import main as real_datasets_main

        real_datasets_main()
        return

    if args.command == "gui":
        if args.type == "desktop":
            from backend.gui.desktop.main_window import main as desktop_main

            desktop_main()
            return

        from backend.gui.web.config import WebGUIConfig
        from backend.gui.web.launcher import WebGUILauncher

        config = WebGUIConfig.from_env()
        if args.host is not None:
            config.host = args.host
        if args.port is not None:
            config.port = args.port
        if args.debug:
            config.debug = True
        if args.no_browser:
            config.auto_open_browser = False

        launcher = WebGUILauncher(config=config)
        launcher.launch()
        return

    raise RuntimeError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
