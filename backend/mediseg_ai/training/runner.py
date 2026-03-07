import logging
from typing import Any, Dict, Optional

import torch
from mediseg_ai.models.unet import UNet

logger = logging.getLogger(__name__)
from mediseg_ai.training.trainer import SegmentationTrainer
from mediseg_ai.utils.common import ConfigLoader
from mediseg_ai.config import get_default_base_config
from mediseg_ai.data_loaders.registry import DatasetRegistry
# Import data loaders to ensure they are registered
import mediseg_ai.data_loaders.pascal_voc
import mediseg_ai.data_loaders.isic


def train_model(
    config_path: str,
    data_dir: str,
    save_dir: str,
    default_template: Optional[dict] = None,
    dataset_kind: str = "pascal_voc",
) -> Optional[Dict[str, Any]]:
    """Train U-Net model on a dataset registered in DatasetRegistry."""
    logger.info("=" * 60)
    logger.info("MediSeg.AI - Training U-Net on %s", dataset_kind)
    logger.info("=" * 60)

    template = default_template if default_template is not None else get_default_base_config()
    config = ConfigLoader.ensure_config(config_path, template)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info("Using device: %s", device)

    model = UNet(
        n_channels=config['model']['in_channels'],
        n_classes=config['model']['num_classes'],
        bilinear=config['model'].get('bilinear', False)
    )
    logger.info("Model created with %s parameters", f"{sum(p.numel() for p in model.parameters()):,}")

    logger.info("Creating data loaders...")

    try:
        create_dataloaders = DatasetRegistry.get(dataset_kind)
    except KeyError as e:
        logger.error("Dataset registry error: %s", e)
        return None

    # Prepare arguments based on dataset kind (this part is still a bit specific, could be improved later)
    common_args = {
        "root_dir": data_dir,
        "batch_size": config['data']['batch_size'],
        "num_workers": config['data']['num_workers'],
        "image_size": tuple(config['data']['image_size']),
    }
    
    if dataset_kind == "isic":
         common_args["train_split"] = config['data'].get('train_split', 0.8)
         common_args["val_split"] = config['data'].get('val_split', 0.1)

    dataloaders = create_dataloaders(**common_args)
    
    if len(dataloaders) == 3:
        train_loader, val_loader, _ = dataloaders
    else:
        train_loader, val_loader = dataloaders
    
    logger.info("Train samples: %s", len(train_loader.dataset))
    logger.info("Validation samples: %s", len(val_loader.dataset))
    
    # Create trainer
    trainer = SegmentationTrainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        config=config,
        save_dir=save_dir
    )
    
    # Start training
    epochs = config['training']['epochs']
    logger.info("Starting training for %s epochs...", epochs)

    summary = trainer.train(epochs)

    logger.info("Training completed!")
    logger.info("Best Dice Score: %.4f", summary['best_dice'])
    logger.info("Final Epoch: %s", summary['final_epoch'])
    
    return summary
