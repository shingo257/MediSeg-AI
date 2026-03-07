"""
DeepLabV3+ implementation for medical image segmentation
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Tuple, Optional
import torchvision.models as models


class ASPP(nn.Module):
    """
    Atrous Spatial Pyramid Pooling module
    """
    
    def __init__(self, in_channels: int, out_channels: int = 256):
        super(ASPP, self).__init__()
        
        # 1x1 convolution
        self.conv1x1 = nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=False)
        self.bn1x1 = nn.BatchNorm2d(out_channels)
        
        # 3x3 convolutions with different dilation rates
        self.conv3x3_1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, 
                                   padding=6, dilation=6, bias=False)
        self.bn3x3_1 = nn.BatchNorm2d(out_channels)
        
        self.conv3x3_2 = nn.Conv2d(in_channels, out_channels, kernel_size=3, 
                                   padding=12, dilation=12, bias=False)
        self.bn3x3_2 = nn.BatchNorm2d(out_channels)
        
        self.conv3x3_3 = nn.Conv2d(in_channels, out_channels, kernel_size=3, 
                                   padding=18, dilation=18, bias=False)
        self.bn3x3_3 = nn.BatchNorm2d(out_channels)
        
        # Global average pooling
        self.global_avg_pool = nn.AdaptiveAvgPool2d(1)
        self.conv_global = nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=False)
        self.bn_global = nn.BatchNorm2d(out_channels)
        
        # Final convolution
        self.conv_final = nn.Conv2d(out_channels * 5, out_channels, kernel_size=1, bias=False)
        self.bn_final = nn.BatchNorm2d(out_channels)
        
        self.relu = nn.ReLU(inplace=True)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        size = x.shape[2:]
        
        # 1x1 convolution
        x1 = self.relu(self.bn1x1(self.conv1x1(x)))
        
        # 3x3 convolutions with different dilation rates
        x2 = self.relu(self.bn3x3_1(self.conv3x3_1(x)))
        x3 = self.relu(self.bn3x3_2(self.conv3x3_2(x)))
        x4 = self.relu(self.bn3x3_3(self.conv3x3_3(x)))
        
        # Global average pooling
        x5 = self.global_avg_pool(x)
        x5 = self.relu(self.bn_global(self.conv_global(x5)))
        x5 = F.interpolate(x5, size=size, mode='bilinear', align_corners=True)
        
        # Concatenate all features
        x = torch.cat([x1, x2, x3, x4, x5], dim=1)
        x = self.relu(self.bn_final(self.conv_final(x)))
        
        return x


class DeepLabV3Plus(nn.Module):
    """
    DeepLabV3+ model for semantic segmentation
    
    Args:
        num_classes: Number of output classes
        backbone: Backbone network ('resnet50', 'resnet101', 'xception')
        pretrained: Whether to use pretrained backbone
        output_stride: Output stride of the model
    """
    
    def __init__(
        self,
        num_classes: int = 1,
        backbone: str = 'resnet50',
        pretrained: bool = True,
        output_stride: int = 16
    ):
        super(DeepLabV3Plus, self).__init__()
        
        self.num_classes = num_classes
        self.backbone_name = backbone
        self.output_stride = output_stride
        
        # Build backbone
        self.backbone = self._build_backbone(backbone, pretrained)
        
        # Get number of channels from backbone
        if backbone in ['resnet50', 'resnet101']:
            low_level_channels = 256
            high_level_channels = 2048
        elif backbone == 'xception':
            low_level_channels = 128
            high_level_channels = 2048
        else:
            raise ValueError(f"Unsupported backbone: {backbone}")
        
        # ASPP module
        self.aspp = ASPP(high_level_channels, 256)
        
        # Decoder
        self.decoder = self._build_decoder(low_level_channels, 256)
        
        # Final classifier
        self.classifier = nn.Conv2d(256, num_classes, kernel_size=1)
        
        # Initialize weights
        self._initialize_weights()
    
    def _build_backbone(self, backbone: str, pretrained: bool) -> nn.Module:
        """Build backbone network"""
        if backbone == 'resnet50':
            model = models.resnet50(pretrained=pretrained)
            # Remove the last two layers (avgpool and fc)
            return nn.Sequential(*list(model.children())[:-2])
        
        elif backbone == 'resnet101':
            model = models.resnet101(pretrained=pretrained)
            return nn.Sequential(*list(model.children())[:-2])
        
        elif backbone == 'xception':
            # Xception backbone (simplified)
            return self._build_xception(pretrained)
        
        else:
            raise ValueError(f"Unsupported backbone: {backbone}")
    
    def _build_xception(self, pretrained: bool) -> nn.Module:
        """Build Xception backbone (simplified version)"""
        # This is a simplified Xception implementation
        # In practice, you would use a proper Xception implementation
        return nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 64, kernel_size=3, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            # Add more layers as needed
        )
    
    def _build_decoder(self, low_level_channels: int, decoder_channels: int) -> nn.Module:
        """Build decoder module"""
        return nn.Sequential(
            nn.Conv2d(low_level_channels, 48, kernel_size=1, bias=False),
            nn.BatchNorm2d(48),
            nn.ReLU(inplace=True),
            nn.Conv2d(48 + decoder_channels, decoder_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(decoder_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(decoder_channels, decoder_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(decoder_channels),
            nn.ReLU(inplace=True)
        )
    
    def _initialize_weights(self):
        """Initialize model weights"""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        input_size = x.shape[2:]
        
        # Extract features from backbone
        features = self.backbone(x)
        
        # Get low-level features (from earlier layers)
        if self.backbone_name in ['resnet50', 'resnet101']:
            # For ResNet, we need to get features from layer 1
            # This is a simplified version - in practice you'd extract from specific layers
            low_level_features = features  # Simplified
        else:
            low_level_features = features  # Simplified
        
        # Apply ASPP
        high_level_features = self.aspp(features)
        
        # Upsample high-level features
        high_level_features = F.interpolate(
            high_level_features, 
            size=low_level_features.shape[2:], 
            mode='bilinear', 
            align_corners=True
        )
        
        # Concatenate with low-level features
        decoder_input = torch.cat([low_level_features, high_level_features], dim=1)
        
        # Apply decoder
        decoder_output = self.decoder(decoder_input)
        
        # Final classification
        output = self.classifier(decoder_output)
        
        # Upsample to input size
        output = F.interpolate(
            output, 
            size=input_size, 
            mode='bilinear', 
            align_corners=True
        )
        
        return output


def create_deeplabv3plus(
    num_classes: int = 1,
    backbone: str = 'resnet50',
    pretrained: bool = True
) -> DeepLabV3Plus:
    """
    Create DeepLabV3+ model
    
    Args:
        num_classes: Number of output classes
        backbone: Backbone network
        pretrained: Whether to use pretrained weights
        
    Returns:
        DeepLabV3+ model
    """
    return DeepLabV3Plus(
        num_classes=num_classes,
        backbone=backbone,
        pretrained=pretrained
    )


def test_deeplabv3plus():
    """Test function for DeepLabV3+ model"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Create model
    model = create_deeplabv3plus(num_classes=1, backbone='resnet50', pretrained=False)
    model = model.to(device)
    
    # Test with random input
    x = torch.randn(2, 3, 256, 256).to(device)
    output = model(x)
    
    print(f"DeepLabV3+ Model Test")
    print(f"Input shape: {x.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"Model size: {sum(p.numel() for p in model.parameters()) * 4 / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    test_deeplabv3plus()
