"""
データローダーファクトリー
"""

from typing import Optional, Dict, Any, Callable, Tuple
from torch.utils.data import DataLoader

from src.data_loaders.base import BaseDatasetLoader
from src.data_loaders.pascal_voc import PascalVOCDataset, create_pascal_voc_dataloaders
from src.data_loaders.isic import ISICDataset, create_isic_dataloaders


class DatasetLoaderFactory:
    """データローダーの生成を統一するファクトリー"""
    
    _loaders: Dict[str, type] = {
        'pascal_voc': PascalVOCDataset,
        'isic': ISICDataset,
    }
    
    _dataloader_creators: Dict[str, Callable] = {
        'pascal_voc': create_pascal_voc_dataloaders,
        'isic': create_isic_dataloaders,
    }
    
    @classmethod
    def create_dataloaders(
        cls,
        dataset_name: str,
        root_dir: str,
        batch_size: int = 16,
        num_workers: int = 4,
        image_size: Optional[Tuple[int, int]] = None
    ) -> Tuple[DataLoader, DataLoader]:
        """
        データローダーを作成
        
        Args:
            dataset_name: データセット名
            root_dir: データディレクトリ
            batch_size: バッチサイズ
            num_workers: ワーカー数
            image_size: 画像サイズ
            
        Returns:
            (訓練データローダー, 検証データローダー)
        """
        if dataset_name not in cls._dataloader_creators:
            raise ValueError(f"Unknown dataset: {dataset_name}")
        
        creator = cls._dataloader_creators[dataset_name]
        return creator(
            root_dir=root_dir,
            batch_size=batch_size,
            num_workers=num_workers,
            image_size=image_size or (256, 256)
        )
    
    @classmethod
    def get_available_datasets(cls) -> list:
        """利用可能なデータセットのリストを取得"""
        return list(cls._loaders.keys())
    
    @classmethod
    def register_dataset(cls, name: str, dataset_class: type, dataloader_creator: Callable):
        """
        新しいデータセットを登録
        
        Args:
            name: データセット名
            dataset_class: データセットクラス
            dataloader_creator: データローダー作成関数
        """
        cls._loaders[name] = dataset_class
        cls._dataloader_creators[name] = dataloader_creator

