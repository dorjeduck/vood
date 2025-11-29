"""CLI commands for the development server"""

import webbrowser
from pathlib import Path

import click

from vood.config import ConfigKey, get_config
from vood.core.logger import get_logger

logger = get_logger()


@click.command(name="serve")
@click.argument("file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "--port",
    "-p",
    type=int,
    default=None,
    help="Server port (default: from config or 8000)",
)
@click.option(
    "--frames",
    "-n",
    type=int,
    default=None,
    help="Number of preview frames (default: from config or 20)",
)
@click.option(
    "--fps",
    "-f",
    type=int,
    default=None,
    help="Playback framerate (default: from config or 10)",
)
@click.option(
    "--no-browser",
    is_flag=True,
    help="Don't automatically open browser",
)
def serve(file: Path, port: int, frames: int, fps: int, no_browser: bool):
    """
    Start development server for live animation preview.

    Watches a Python animation file and provides live browser preview with
    automatic hot-reload on file changes.

    Example:
        vood serve examples/my_animation.py
        vood serve animation.py --port 8080 --frames 30 --fps 30
    """
    # Load config
    config = get_config()

    # Use CLI args or fall back to config/defaults
    port = port or config.get(ConfigKey.DEVSERVER_PORT, 8000)
    frames = frames or config.get(ConfigKey.DEVSERVER_DEFAULT_FRAMES, 20)
    fps = fps or config.get(ConfigKey.DEVSERVER_DEFAULT_FPS, 10)
    auto_open = not no_browser and config.get(ConfigKey.DEVSERVER_AUTO_OPEN_BROWSER, True)

    # Convert fps to interval (milliseconds between frames)
    interval = int(1000 / fps)

    # Check dependencies
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
        import watchdog  # noqa: F401
    except ImportError as e:
        click.echo(
            "✗ Dev server dependencies not installed. Install with:", err=True
        )
        click.echo("  pip install vood[devserver]", err=True)
        click.echo(f"\nMissing: {e.name}", err=True)
        raise click.Abort()

    # Import server components (after dependency check)
    from vood.server.dev.server import create_app

    # Validate file
    file = file.resolve()
    if not file.suffix == ".py":
        click.echo("✗ File must be a Python file (.py)", err=True)
        raise click.Abort()

    # Create server
    click.echo(f"Starting Vood development server...")
    click.echo(f"  File: {file}")
    click.echo(f"  Port: {port}")
    click.echo(f"  Frames: {frames}")
    click.echo(f"  FPS: {fps}")
    click.echo()

    app, dev_server = create_app(
        file_path=file,
        num_frames=frames,
        play_interval_ms=interval,
        port=port,
    )

    # Start file watching
    dev_server.start_watching()

    # Open browser
    if auto_open:
        url = f"http://localhost:{port}"
        click.echo(f"Opening browser: {url}")
        webbrowser.open(url)
        click.echo()

    # Start server
    click.echo("Server running. Press Ctrl+C to stop.")
    click.echo(f"View at: http://localhost:{port}")
    click.echo()

    try:
        import uvicorn

        # Run server (blocking)
        uvicorn.run(
            app,
            host="localhost",
            port=port,
            log_level="warning",  # Reduce noise, our logger handles important messages
        )
    except KeyboardInterrupt:
        click.echo("\n\nShutting down...")
    finally:
        dev_server.stop_watching()
        click.echo("Server stopped.")
