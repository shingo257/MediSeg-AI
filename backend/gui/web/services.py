"""
Web GUI business logic: model loading, segmentation, visualization.
Routes and launcher import from here to avoid circular dependency on web_gui.
"""

import base64
import io
import logging
from typing import Any, Dict, Optional, Tuple

import cv2

logger = logging.getLogger(__name__)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import torch

from backend.gui.web import state as app_state
from mediseg_ai.models.unet import UNet
from mediseg_ai.models.deeplabv3plus import create_deeplabv3plus
from mediseg_ai.utils.exceptions import ModelLoadError


def setup_models() -> bool:
    """Load U-Net and DeepLabV3+ into app state; returns True on success."""
    try:
        app_state.models['U-Net'] = UNet(n_channels=3, n_classes=1, bilinear=False)
        app_state.models['DeepLabV3+'] = create_deeplabv3plus(
            num_classes=1, backbone='resnet50', pretrained=False
        )
        logger.info("Models loaded successfully")
        return True
    except Exception as e:
        logger.exception("Failed to load models: %s", e)
        raise ModelLoadError(str(e)) from e


def process_image(
    image_path: str, model_type: str, threshold: float = 0.5
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Run segmentation on image; returns (results_dict, None) or (None, error_message)."""
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None, "Failed to load image"
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        app_state.current_image = image.copy()
        if model_type not in app_state.models:
            return None, f"Model {model_type} not available"
        model = app_state.models[model_type]

        image_tensor = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0
        image_tensor = image_tensor.unsqueeze(0)

        model.eval()
        with torch.no_grad():
            prediction = model(image_tensor)

        prediction = torch.sigmoid(prediction).squeeze().cpu().numpy()
        binary_mask = (prediction > threshold).astype(np.uint8)
        results = {}

        app_state.current_results = {
            'prediction': prediction,
            'binary_mask': binary_mask,
            'metrics': results,
            'model_type': model_type,
            'threshold': threshold
        }
        return app_state.current_results, None

    except Exception as e:
        return None, str(e)


def create_visualization(
    image: np.ndarray,
    prediction: np.ndarray,
    mask: np.ndarray,
    metrics: Dict[str, Any],
) -> str:
    """Create 2x2 visualization figure; returns base64-encoded PNG string."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.patch.set_facecolor('#2b2b2b')

    axes[0, 0].imshow(image)
    axes[0, 0].set_title('Original Image', color='white', fontsize=14, fontweight='bold')
    axes[0, 0].axis('off')

    im1 = axes[0, 1].imshow(prediction, cmap='viridis')
    axes[0, 1].set_title('Prediction Heatmap', color='white', fontsize=14, fontweight='bold')
    axes[0, 1].axis('off')
    plt.colorbar(im1, ax=axes[0, 1], fraction=0.046, pad=0.04)

    axes[1, 0].imshow(mask, cmap='gray')
    axes[1, 0].set_title('Binary Mask', color='white', fontsize=14, fontweight='bold')
    axes[1, 0].axis('off')

    overlay = image.copy()
    overlay[mask > 0] = [255, 0, 0]
    axes[1, 1].imshow(overlay)
    axes[1, 1].set_title('Overlay', color='white', fontsize=14, fontweight='bold')
    axes[1, 1].axis('off')

    metrics_text = f"""
Model: {metrics.get('model_type', 'Unknown')}
Dice: {metrics.get('dice', 0.0):.3f}
IoU: {metrics.get('iou', 0.0):.3f}
Accuracy: {metrics.get('accuracy', 0.0):.3f}
Sensitivity: {metrics.get('sensitivity', 0.0):.3f}
Specificity: {metrics.get('specificity', 0.0):.3f}
    """

    fig.text(0.02, 0.02, metrics_text, fontsize=10, color='white',
             bbox=dict(boxstyle="round,pad=0.3", facecolor='#404040', alpha=0.8))

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight',
                facecolor='#2b2b2b', edgecolor='none')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return image_base64


def generate_mask_image() -> str:
    """Generate a simple mask image; returns base64-encoded PNG."""
    mask = np.random.rand(256, 256) > 0.7
    from PIL import Image
    mask_img = Image.fromarray((mask * 255).astype(np.uint8))
    buffer = io.BytesIO()
    mask_img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()


def generate_contour_image() -> str:
    """Generate a simple contour image; returns base64-encoded PNG."""
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (256, 256), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([50, 50, 206, 206], outline=(255, 0, 0), width=3)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()
