"""
Vood Development Server

Lightweight development server for live animation preview with hot-reload.
"""

from .module_loader import animation
from .server import create_app

__all__ = ["create_app", "animation"]
