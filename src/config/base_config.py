"""
基本設定クラス
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class BaseConfig:
    """基本設定クラス"""
    
    def to_dict(self) -> Dict[str, Any]:
        """設定を辞書に変換"""
        return {
            key: value
            for key, value in self.__dict__.items()
            if not key.startswith('_')
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseConfig':
        """辞書から設定を作成"""
        return cls(**data)
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        """
        設定の検証
        
        Returns:
            (検証成功, エラーメッセージ)
        """
        return True, None

