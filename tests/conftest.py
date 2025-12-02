"""
Pytest設定と共通フィクスチャ
"""

import pytest
import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_image_path(tmp_path):
    """サンプル画像パスのフィクスチャ"""
    # 実際のテストでは、テスト用の画像ファイルを作成
    return str(tmp_path / "test_image.jpg")


@pytest.fixture
def sample_config():
    """サンプル設定のフィクスチャ"""
    return {
        'model': {
            'in_channels': 3,
            'num_classes': 1,
            'bilinear': False
        },
        'data': {
            'batch_size': 16,
            'num_workers': 4,
            'image_size': [256, 256]
        },
        'training': {
            'epochs': 10,
            'learning_rate': 0.001,
            'optimizer': 'adam'
        }
    }

