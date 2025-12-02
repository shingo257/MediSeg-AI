"""
カスタム例外クラス
"""


class MediSegError(Exception):
    """MediSeg.AIの基底例外クラス"""
    pass


class ModelError(MediSegError):
    """モデル関連のエラー"""
    pass


class DatasetError(MediSegError):
    """データセット関連のエラー"""
    pass


class ImageProcessingError(MediSegError):
    """画像処理関連のエラー"""
    pass


class ValidationError(MediSegError):
    """検証関連のエラー"""
    pass


class ConfigurationError(MediSegError):
    """設定関連のエラー"""
    pass

