"""
Advanced data augmentation techniques for medical images
"""

import torch
import numpy as np
import cv2
from typing import Tuple, Dict, Any
import albumentations as A
from albumentations.pytorch import ToTensorV2


class MedicalImageAugmentation:
    """
    Advanced augmentation techniques specifically designed for medical images
    """
    
    def __init__(self, image_size: Tuple[int, int] = (256, 256)):
        self.image_size = image_size
    
    def get_training_augmentations(self) -> A.Compose:
        """
        Get comprehensive training augmentations for medical images
        
        Returns:
            Albumentations compose transform
        """
        return A.Compose([
            # Resize to target size
            A.Resize(self.image_size[0], self.image_size[1]),
            
            # Geometric transformations
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
            A.Rotate(limit=45, p=0.5),
            A.ShiftScaleRotate(
                shift_limit=0.1,
                scale_limit=0.2,
                rotate_limit=45,
                p=0.5
            ),
            
            # Elastic deformations (important for medical images)
            A.ElasticTransform(
                alpha=1,
                sigma=50,
                alpha_affine=50,
                p=0.3
            ),
            
            # Grid distortion
            A.GridDistortion(
                num_steps=5,
                distort_limit=0.3,
                p=0.3
            ),
            
            # Optical distortion
            A.OpticalDistortion(
                distort_limit=0.3,
                shift_limit=0.1,
                p=0.3
            ),
            
            # Color space transformations
            A.RandomBrightnessContrast(
                brightness_limit=0.3,
                contrast_limit=0.3,
                p=0.5
            ),
            A.RandomGamma(
                gamma_limit=(80, 120),
                p=0.5
            ),
            A.HueSaturationValue(
                hue_shift_limit=20,
                sat_shift_limit=30,
                val_shift_limit=20,
                p=0.5
            ),
            
            # Noise and blur
            A.GaussNoise(
                var_limit=(10.0, 50.0),
                p=0.3
            ),
            A.GaussianBlur(
                blur_limit=3,
                p=0.3
            ),
            A.MotionBlur(
                blur_limit=3,
                p=0.3
            ),
            
            # Advanced augmentations for medical images
            A.CLAHE(
                clip_limit=4.0,
                tile_grid_size=(8, 8),
                p=0.3
            ),
            A.RandomShadow(
                shadow_roi=(0, 0.5, 1, 1),
                num_shadows_lower=1,
                num_shadows_upper=2,
                shadow_dimension=5,
                p=0.3
            ),
            
            # Normalize
            A.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
            ToTensorV2()
        ])
    
    def get_validation_augmentations(self) -> A.Compose:
        """
        Get validation augmentations (minimal)
        
        Returns:
            Albumentations compose transform
        """
        return A.Compose([
            A.Resize(self.image_size[0], self.image_size[1]),
            A.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
            ToTensorV2()
        ])
    
    def get_test_time_augmentation(self) -> A.Compose:
        """
        Get test time augmentation for robust predictions
        
        Returns:
            Albumentations compose transform
        """
        return A.Compose([
            A.Resize(self.image_size[0], self.image_size[1]),
            A.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
            ToTensorV2()
        ])


class MedicalImagePreprocessing:
    """
    Preprocessing techniques for medical images
    """
    
    @staticmethod
    def enhance_contrast(image: np.ndarray, method: str = 'clahe') -> np.ndarray:
        """
        Enhance contrast of medical images
        
        Args:
            image: Input image
            method: Enhancement method ('clahe', 'histogram_eq', 'gamma')
            
        Returns:
            Enhanced image
        """
        if method == 'clahe':
            clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
            if len(image.shape) == 3:
                # Convert to LAB color space
                lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
                lab[:, :, 0] = clahe.apply(lab[:, :, 0])
                return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            else:
                return clahe.apply(image)
        
        elif method == 'histogram_eq':
            if len(image.shape) == 3:
                # Convert to YUV color space
                yuv = cv2.cvtColor(image, cv2.COLOR_RGB2YUV)
                yuv[:, :, 0] = cv2.equalizeHist(yuv[:, :, 0])
                return cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB)
            else:
                return cv2.equalizeHist(image)
        
        elif method == 'gamma':
            gamma = 1.5
            lookup_table = np.array([((i / 255.0) ** (1.0 / gamma)) * 255
                                   for i in np.arange(0, 256)]).astype("uint8")
            return cv2.LUT(image, lookup_table)
        
        else:
            return image
    
    @staticmethod
    def remove_background(image: np.ndarray, threshold: int = 10) -> np.ndarray:
        """
        Remove background from medical images
        
        Args:
            image: Input image
            threshold: Threshold for background detection
            
        Returns:
            Image with background removed
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Create mask for background
        mask = gray > threshold
        
        # Apply mask
        result = image.copy()
        result[~mask] = 0
        
        return result
    
    @staticmethod
    def normalize_intensity(image: np.ndarray, method: str = 'zscore') -> np.ndarray:
        """
        Normalize intensity of medical images
        
        Args:
            image: Input image
            method: Normalization method ('zscore', 'minmax', 'robust')
            
        Returns:
            Normalized image
        """
        if method == 'zscore':
            mean = np.mean(image)
            std = np.std(image)
            return (image - mean) / (std + 1e-8)
        
        elif method == 'minmax':
            min_val = np.min(image)
            max_val = np.max(image)
            return (image - min_val) / (max_val - min_val + 1e-8)
        
        elif method == 'robust':
            # Use median and IQR for robust normalization
            median = np.median(image)
            q75, q25 = np.percentile(image, [75, 25])
            iqr = q75 - q25
            return (image - median) / (iqr + 1e-8)
        
        else:
            return image


def create_medical_augmentation_pipeline(
    image_size: Tuple[int, int] = (256, 256),
    augmentation_strength: str = 'medium'
) -> Dict[str, A.Compose]:
    """
    Create comprehensive augmentation pipeline for medical images
    
    Args:
        image_size: Target image size
        augmentation_strength: Strength of augmentations ('light', 'medium', 'heavy')
        
    Returns:
        Dictionary containing different augmentation pipelines
    """
    augmenter = MedicalImageAugmentation(image_size)
    
    pipelines = {
        'train': augmenter.get_training_augmentations(),
        'val': augmenter.get_validation_augmentations(),
        'test': augmenter.get_validation_augmentations(),
        'tta': augmenter.get_test_time_augmentation()
    }
    
    # Adjust augmentation strength
    if augmentation_strength == 'light':
        # Reduce probability of strong augmentations
        pass  # Use default probabilities
    elif augmentation_strength == 'heavy':
        # Increase probability of strong augmentations
        pass  # Use default probabilities
    
    return pipelines


def test_medical_augmentations():
    """Test function for medical augmentations"""
    print("Medical Image Augmentation Test")
    
    # Create dummy image
    dummy_image = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
    dummy_mask = np.random.randint(0, 2, (256, 256), dtype=np.uint8)
    
    # Test augmentation pipeline
    pipelines = create_medical_augmentation_pipeline()
    
    print("Available pipelines:")
    for name, pipeline in pipelines.items():
        print(f"- {name}: {len(pipeline.transforms)} transforms")
    
    # Test preprocessing
    preprocessor = MedicalImagePreprocessing()
    
    # Test contrast enhancement
    enhanced = preprocessor.enhance_contrast(dummy_image, 'clahe')
    print(f"Contrast enhancement: {dummy_image.shape} -> {enhanced.shape}")
    
    # Test background removal
    no_bg = preprocessor.remove_background(dummy_image)
    print(f"Background removal: {dummy_image.shape} -> {no_bg.shape}")
    
    # Test intensity normalization
    normalized = preprocessor.normalize_intensity(dummy_image, 'zscore')
    print(f"Intensity normalization: {dummy_image.shape} -> {normalized.shape}")
    
    print("Medical augmentation test completed!")


if __name__ == "__main__":
    test_medical_augmentations()
