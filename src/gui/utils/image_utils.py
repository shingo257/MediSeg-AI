"""
画像処理ユーティリティ
"""

import os
import cv2
import numpy as np
import base64
from typing import Optional

# サポートされている画像拡張子
EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.dcm', '.nii', '.nii.gz')


def to_thumbnail_b64(img_rgb: np.ndarray, max_side: int = 200) -> str:
    """
    画像をサムネイル化してBase64エンコード
    
    Args:
        img_rgb: RGB画像（numpy配列）
        max_side: 最大サイズ（ピクセル）
        
    Returns:
        Base64エンコードされた画像文字列
    """
    h, w = img_rgb.shape[:2]
    scale = max_side / max(h, w)
    new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
    thumb = cv2.resize(img_rgb, (new_w, new_h))
    _, buf = cv2.imencode('.png', cv2.cvtColor(thumb, cv2.COLOR_RGB2BGR))
    return base64.b64encode(buf).decode()


def load_image_any(path: str) -> Optional[np.ndarray]:
    """
    様々なフォーマットの画像を読み込む
    
    サポートフォーマット:
    - JPEG, PNG, BMP, TIFF
    - DICOM (.dcm)
    - NIfTI (.nii, .nii.gz)
    
    Args:
        path: 画像ファイルのパス
        
    Returns:
        RGB画像（numpy配列）、読み込み失敗時はNone
    """
    lower = path.lower()
    try:
        # 標準画像フォーマット
        if lower.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff')):
            img = cv2.imread(path)
            if img is None:
                return None
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # DICOMフォーマット
        if lower.endswith('.dcm'):
            try:
                import pydicom  # type: ignore
            except ImportError:
                return None
            ds = pydicom.dcmread(path, force=True)
            arr = ds.pixel_array.astype(np.float32)
            # 窓設定（簡易正規化）
            arr -= arr.min()
            if arr.max() > 0:
                arr /= arr.max()
            arr = (arr * 255).astype(np.uint8)
            return np.stack([arr, arr, arr], axis=-1)
        
        # NIfTIフォーマット
        if lower.endswith(('.nii', '.nii.gz')):
            try:
                import nibabel as nib  # type: ignore
            except ImportError:
                return None
            img = nib.load(path)
            data = np.asanyarray(img.dataobj)
            # 中央スライスを取り出し（軸は簡易推定）
            if data.ndim == 3:
                z = data.shape[2] // 2
                sl = data[:, :, z]
            elif data.ndim == 4:
                z = data.shape[2] // 2
                sl = data[:, :, z, 0]
            else:
                return None
            sl = sl.astype(np.float32)
            sl -= sl.min()
            if sl.max() > 0:
                sl /= sl.max()
            sl = (sl * 255).astype(np.uint8)
            return np.stack([sl, sl, sl], axis=-1)
    except Exception:
        return None
    return None


def has_any_images(path: str) -> bool:
    """
    指定パスに画像ファイルが存在するかチェック
    
    Args:
        path: チェックするパス
        
    Returns:
        画像ファイルが存在する場合True
    """
    if not path or not os.path.exists(path):
        return False
    exts = EXTENSIONS
    for root, _, files in os.walk(path):
        for f in files:
            if f.lower().endswith(exts):
                return True
    return False

