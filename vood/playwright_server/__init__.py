"""Playwright-based HTTP rendering server for SVG to PNG/PDF conversion

This module provides a lightweight HTTP server that uses Playwright's headless
Chromium browser to render SVG content to PNG and PDF formats.

The server is designed to run as a background daemon process and can be
managed via CLI commands or auto-started by the PlaywrightHttpSvgConverter.
"""

from .render_server import app, create_server
from .process_manager import ProcessManager

__all__ = ["app", "create_server", "ProcessManager"]
