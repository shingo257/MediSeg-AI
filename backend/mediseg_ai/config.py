import copy
from pydantic import BaseModel, Field
from typing import List, Optional

class DataConfig(BaseModel):
    batch_size: int = 8
    num_workers: int = 4
    image_size: List[int] = [256, 256]
    augmentation: bool = True
    train_split: float = 0.8
    val_split: float = 0.1
    data_dir: Optional[str] = None

class ModelConfig(BaseModel):
    name: str = "unet"
    encoder: str = "resnet34"
    encoder_weights: str = "imagenet"
    in_channels: int = 3
    classes: int = 1

class TrainingConfig(BaseModel):
    epochs: int = 50
    learning_rate: float = 1e-4
    optimizer: str = "adam"
    scheduler: str = "plateau"
    loss: str = "dice_loss"
    device: str = "cuda"

class LoggingConfig(BaseModel):
    use_wandb: bool = False
    use_tensorboard: bool = False
    log_interval: int = 10
    save_interval: int = 5

class MedicalConfig(BaseModel):
    dataset: str = "isic"
    lesion_type: str = "melanoma"
    elastic_transform: bool = True
    grid_distortion: bool = True
    gamma_correction: bool = True

class Settings(BaseModel):
    data: DataConfig = Field(default_factory=DataConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    training: TrainingConfig = Field(default_factory=TrainingConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    medical: MedicalConfig = Field(default_factory=MedicalConfig)

settings = Settings()


def get_default_base_config() -> dict:
    """Pascal VOC 用のデフォルト設定（config ファイルが無いときのテンプレート）。"""
    config = copy.deepcopy(settings.model_dump())
    config["data"].update({"batch_size": 16})
    config["training"].update({
        "epochs": 100,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "scheduler": "cosine",
    })
    config["evaluation"] = {
        "metrics": ["iou", "dice", "accuracy"],
        "save_predictions": True,
        "visualize": True,
    }
    return config


def get_default_isic_config() -> dict:
    """ISIC / train-medical 用のデフォルト設定。"""
    config = copy.deepcopy(settings.model_dump())
    config["training"].update({"epochs": 150, "loss": "combined"})
    config["evaluation"] = {
        "metrics": ["dice", "iou", "accuracy", "sensitivity", "specificity"],
        "save_predictions": True,
        "visualize": True,
    }
    return config
