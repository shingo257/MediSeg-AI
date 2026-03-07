import logging
from typing import Any, Dict

import torch
from mediseg_ai.models.unet import UNet
from mediseg_ai.evaluation.evaluate import ModelEvaluator
from mediseg_ai.data_loaders.pascal_voc import PascalVOCDataset, get_pascal_voc_transforms

logger = logging.getLogger(__name__)


def evaluate_model(model_path: str, data_dir: str, save_dir: str) -> Dict[str, Any]:
    """Evaluate trained model; returns evaluation metrics dict."""
    logger.info("=" * 60)
    logger.info("MediSeg.AI - Evaluating Trained Model")
    logger.info("=" * 60)

    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info("Using device: %s", device)

    # Load model
    logger.info("Loading model from: %s", model_path)
    try:
        checkpoint = torch.load(model_path, map_location=device, weights_only=False)
    except TypeError:
        checkpoint = torch.load(model_path, map_location=device)
    config = checkpoint['config']
    
    model = UNet(
        n_channels=config['model']['in_channels'],
        n_classes=config['model']['num_classes'],
        bilinear=config['model'].get('bilinear', False)
    )
    model.load_state_dict(checkpoint['model_state_dict'])
    
    logger.info("Model loaded with %s parameters", f"{sum(p.numel() for p in model.parameters()):,}")
    
    # Create test dataset (currently Pascal VOC only; generic registry/test_loader can be added later)
    test_transform = get_pascal_voc_transforms(
        image_size=tuple(config['data']['image_size']),
        is_training=False
    )
    
    test_dataset = PascalVOCDataset(
        root_dir=data_dir,
        split='test',
        transform=test_transform
    )
    
    test_loader = torch.utils.data.DataLoader(
        test_dataset,
        batch_size=config['data']['batch_size'],
        shuffle=False,
        num_workers=config['data']['num_workers'],
        pin_memory=True
    )
    
    logger.info("Test samples: %s", len(test_dataset))
    
    # Create evaluator
    evaluator = ModelEvaluator(
        model=model,
        test_loader=test_loader,
        device=device,
        save_dir=save_dir
    )
    
    # Run evaluation
    results = evaluator.evaluate()
    
    # Save results
    evaluator.save_results(results)
    
    logger.info("Evaluation completed!")
    return results
