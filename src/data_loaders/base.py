"""
ベースデータローダークラス
"""

from abc import ABC, abstractmethod
from torch.utils.data import Dataset, DataLoader
from typing import Optional, Tuple, Dict, Any
import torch


class BaseDatasetLoader(ABC):
    """データローダーのベースクラス"""
    
    @abstractmethod
    def get_dataset(
        self,
        split: str = 'train',
        transform: Optional[Any] = None
    ) -> Dataset:
        """
        データセットを取得
        
        Args:
            split: データセットの分割 ('train', 'val', 'test')
            transform: 変換関数
            
        Returns:
            データセット
        """
        pass
    
    @abstractmethod
    def get_dataloader(
        self,
        split: str = 'train',
        batch_size: int = 16,
        num_workers: int = 4,
        shuffle: bool = True,
        transform: Optional[Any] = None
    ) -> DataLoader:
        """
        データローダーを取得
        
        Args:
            split: データセットの分割
            batch_size: バッチサイズ
            num_workers: ワーカー数
            shuffle: シャッフルするか
            transform: 変換関数
            
        Returns:
            データローダー
        """
        pass
    
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """
        データセット情報を取得
        
        Returns:
            データセット情報
        """
        pass

