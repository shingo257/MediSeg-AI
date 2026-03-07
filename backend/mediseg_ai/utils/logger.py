"""
Simple logging helpers used across the project.
"""

from __future__ import annotations

import logging
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger.

    This keeps logging lightweight (no external deps) and avoids duplicate handlers.
    """
    logger = logging.getLogger(name)

    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )

    return logger

