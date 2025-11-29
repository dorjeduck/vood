"""Centralized logging configuration for vood package."""

import logging
from pathlib import Path
from typing import Optional

# Single logger instance for the entire package
_logger = logging.getLogger("vood")
_logger.setLevel(logging.DEBUG)  # Capture everything, filter at handler level
_logger.propagate = False


def configure_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    console: bool = True,
    silent: bool = False,
):
    """Configure logging for the vood package.

    Args:
        level: Log level - "DEBUG", "INFO", "WARNING", or "ERROR" (default: from config)
        log_file: Path to log file (None to disable file logging)
        console: Whether to log to console (ignored if silent=True)
        silent: If True, disables all console output (file logging still works)

    Example:
        # Console only, INFO level (or config default)
        configure_logging()

        # Explicit level
        configure_logging(level="DEBUG")

        # File only, DEBUG level
        configure_logging(level="DEBUG", log_file="vood.log", console=False)

        # Silent mode with file logging
        configure_logging(silent=True, log_file="vood.log")

        # Completely silent
        configure_logging(silent=True)
    """
    # Clear existing handlers
    _logger.handlers.clear()

    # Get level from config if not specified
    if level is None:
        from vood.config import get_config, ConfigKey
        config = get_config()
        level = config.get(ConfigKey.LOGGING_LEVEL, 'INFO')

    # Convert level string to logging constant
    log_level = getattr(logging, level.upper(), logging.INFO)
    _logger.setLevel(log_level)

    # Add console handler (unless silent)
    if console and not silent:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
        console_handler.setFormatter(console_formatter)
        _logger.addHandler(console_handler)

    # Add file handler if requested
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # File gets full detail
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler.setFormatter(file_formatter)
        _logger.addHandler(file_handler)

    # If no handlers added, add NullHandler to prevent warnings
    if not _logger.handlers:
        _logger.addHandler(logging.NullHandler())


def get_logger() -> logging.Logger:
    """Get the vood logger instance.

    Returns:
        The configured logger for the vood package
    """
    # Ensure logger has at least a NullHandler if never configured
    if not _logger.handlers:
        _logger.addHandler(logging.NullHandler())
    return _logger


# Initialize with default configuration (NullHandler)
if not _logger.handlers:
    _logger.addHandler(logging.NullHandler())
