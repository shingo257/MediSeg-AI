"""
MediSeg.AI custom exceptions.
CLI and Web GUI share these for consistent error handling.
"""


class MediSegError(Exception):
    """Base exception for MediSeg.AI."""

    pass


class ValidationError(ValueError, MediSegError):
    """Raised when input validation fails (CLI args, request payload, etc.)."""

    pass


class ModelLoadError(MediSegError):
    """Raised when model loading fails (file missing, checkpoint invalid, etc.)."""

    pass


class DatasetError(MediSegError):
    """Raised when dataset access or preparation fails."""

    pass


class ConfigError(MediSegError):
    """Raised when configuration is invalid or missing."""

    pass
