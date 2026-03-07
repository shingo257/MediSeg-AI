from typing import Callable, Dict, Any, Tuple
from torch.utils.data import DataLoader

class DatasetRegistry:
    """Registry for dataset loaders"""
    _registry: Dict[str, Callable[..., Tuple[DataLoader, ...]]] = {}

    @classmethod
    def register(cls, name: str) -> Callable:
        """Decorator to register a dataset loader"""
        def decorator(func: Callable[..., Tuple[DataLoader, ...]]):
            cls._registry[name] = func
            return func
        return decorator

    @classmethod
    def get(cls, name: str) -> Callable[..., Tuple[DataLoader, ...]]:
        """Get a dataset loader by name"""
        if name not in cls._registry:
            raise KeyError(f"Dataset '{name}' not found in registry. Available: {list(cls._registry.keys())}")
        return cls._registry[name]

    @classmethod
    def list_datasets(cls):
        """List registered datasets"""
        return list(cls._registry.keys())
