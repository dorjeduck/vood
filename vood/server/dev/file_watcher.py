"""
File watching with debouncing for development server.

Monitors Python animation files and triggers reloads on changes.
"""

import asyncio
import time
from pathlib import Path
from typing import Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent


class DebouncedFileHandler(FileSystemEventHandler):
    """
    File system event handler with debouncing.

    Debouncing prevents rapid successive reloads when a file is modified multiple times
    in quick succession (e.g., during save operations).
    """

    def __init__(
        self,
        file_path: Path,
        on_change_callback: Callable[[], None],
        debounce_ms: int = 200,
    ):
        """
        Initialize debounced file handler.

        Args:
            file_path: Path to the file to watch
            on_change_callback: Callback to invoke when file changes (after debounce)
            debounce_ms: Debounce delay in milliseconds (default: 200ms)
        """
        super().__init__()
        self.file_path = file_path.resolve()
        self.on_change_callback = on_change_callback
        self.debounce_seconds = debounce_ms / 1000.0
        self.last_modified_time = 0.0
        self.pending_task: Optional[asyncio.Task] = None

    def on_modified(self, event):
        """
        Handle file modification events.

        Args:
            event: The file system event
        """
        # Only process .py file changes
        if event.is_directory or not event.src_path.endswith(".py"):
            return

        # Check if this is the file we're watching
        event_path = Path(event.src_path).resolve()
        if event_path != self.file_path:
            return

        current_time = time.time()

        # Debounce: ignore if too soon after last modification
        if current_time - self.last_modified_time < self.debounce_seconds:
            return

        self.last_modified_time = current_time

        # Trigger callback
        self.on_change_callback()


class FileWatcher:
    """
    Watches a Python animation file for changes and triggers reloads.
    """

    def __init__(
        self,
        file_path: Path,
        on_change_callback: Callable[[], None],
        debounce_ms: int = 200,
    ):
        """
        Initialize file watcher.

        Args:
            file_path: Path to the Python file to watch
            on_change_callback: Callback to invoke when file changes
            debounce_ms: Debounce delay in milliseconds
        """
        self.file_path = file_path.resolve()
        self.on_change_callback = on_change_callback
        self.debounce_ms = debounce_ms

        # Create handler and observer
        self.handler = DebouncedFileHandler(
            file_path=self.file_path,
            on_change_callback=on_change_callback,
            debounce_ms=debounce_ms,
        )

        self.observer = Observer()

        # Watch the parent directory (watchdog can't watch individual files)
        watch_dir = self.file_path.parent
        self.observer.schedule(self.handler, str(watch_dir), recursive=False)

    def start(self):
        """Start watching for file changes."""
        self.observer.start()

    def stop(self):
        """Stop watching for file changes."""
        self.observer.stop()
        self.observer.join()
