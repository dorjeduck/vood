"""Cross-platform process manager for Playwright render server daemon

Handles starting, stopping, and monitoring the server process across
Linux, macOS, and Windows using PID files and psutil for process control.
"""

from __future__ import annotations

import os
import sys
import time
import subprocess
import signal
from pathlib import Path
from typing import Optional, Dict, Any

import psutil

from vood.core.logger import get_logger

logger = get_logger()


class ProcessManager:
    """Manages the Playwright render server as a background daemon process"""

    def __init__(
        self,
        pid_file: Optional[Path] = None,
        log_file: Optional[Path] = None,
        host: str = "localhost",
        port: int = 4000,
    ):
        """Initialize process manager

        Args:
            pid_file: Path to PID file (default: ~/.vood/playwright-server.pid)
            log_file: Path to log file (default: ~/.vood/playwright-server.log)
            host: Server host (default: localhost)
            port: Server port (default: 4000)
        """
        vood_dir = Path.home() / ".vood"
        vood_dir.mkdir(exist_ok=True)

        self.pid_file = pid_file or vood_dir / "playwright-server.pid"
        self.log_file = log_file or vood_dir / "playwright-server.log"
        self.host = host
        self.port = port

    def is_running(self) -> bool:
        """Check if server is currently running

        Returns:
            True if server process is running, False otherwise
        """
        pid = self._read_pid()
        if pid is None:
            return False

        try:
            process = psutil.Process(pid)
            # Verify it's our server by checking command line
            cmdline = " ".join(process.cmdline())
            return "playwright" in cmdline.lower() and "render" in cmdline.lower()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Process doesn't exist or can't access it
            self._remove_pid_file()
            return False

    def start(self) -> bool:
        """Start the server as a background daemon

        Returns:
            True if started successfully, False if already running or failed

        Raises:
            RuntimeError: If server fails to start
        """
        if self.is_running():
            logger.info("Playwright server is already running")
            return False

        logger.info(f"Starting Playwright server on {self.host}:{self.port}")

        try:
            # Find the python executable
            python_exe = sys.executable

            # Build command to run uvicorn with our FastAPI app
            cmd = [
                python_exe,
                "-m",
                "uvicorn",
                "vood.playwright_server.render_server:app",
                "--host",
                self.host,
                "--port",
                str(self.port),
                "--log-level",
                "info",
            ]

            # Open log file for output
            log_fd = open(self.log_file, "a")

            # Platform-specific daemon spawning
            if sys.platform == "win32":
                # Windows: Use CREATE_NEW_PROCESS_GROUP and DETACHED_PROCESS
                CREATE_NEW_PROCESS_GROUP = 0x00000200
                DETACHED_PROCESS = 0x00000008
                process = subprocess.Popen(
                    cmd,
                    stdout=log_fd,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL,
                    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                )
            else:
                # Unix: Use double-fork pattern for proper daemonization
                process = subprocess.Popen(
                    cmd,
                    stdout=log_fd,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True,  # Detach from parent session
                )

            # Write PID file
            self._write_pid(process.pid)

            # Wait a moment and verify it's still running
            time.sleep(2)
            if not self.is_running():
                raise RuntimeError("Server process died immediately after start")

            logger.info(f"Playwright server started with PID {process.pid}")
            return True

        except Exception as e:
            logger.error(f"Failed to start Playwright server: {e}")
            self._remove_pid_file()
            raise

    def stop(self) -> bool:
        """Stop the running server gracefully

        Returns:
            True if stopped successfully, False if not running
        """
        pid = self._read_pid()
        if pid is None:
            logger.info("Playwright server is not running")
            return False

        try:
            process = psutil.Process(pid)

            # Try graceful shutdown first (SIGTERM on Unix, TerminateProcess on Windows)
            logger.info(f"Stopping Playwright server (PID {pid})")
            process.terminate()

            # Wait up to 10 seconds for graceful shutdown
            try:
                process.wait(timeout=10)
            except psutil.TimeoutExpired:
                # Force kill if still running
                logger.warning("Graceful shutdown timeout, forcing kill")
                process.kill()
                process.wait(timeout=5)

            self._remove_pid_file()
            logger.info("Playwright server stopped")
            return True

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.warning(f"Process not found or access denied: {e}")
            self._remove_pid_file()
            return False

    def restart(self) -> bool:
        """Restart the server (stop then start)

        Returns:
            True if restarted successfully
        """
        self.stop()
        time.sleep(1)
        return self.start()

    def status(self) -> Dict[str, Any]:
        """Get detailed server status

        Returns:
            Dictionary with status information:
            - running: bool
            - pid: int or None
            - uptime_seconds: float or None
            - memory_mb: float or None
        """
        pid = self._read_pid()
        if pid is None or not self.is_running():
            return {
                "running": False,
                "pid": None,
                "uptime_seconds": None,
                "memory_mb": None,
            }

        try:
            process = psutil.Process(pid)
            uptime = time.time() - process.create_time()
            memory_mb = process.memory_info().rss / (1024 * 1024)

            return {
                "running": True,
                "pid": pid,
                "uptime_seconds": uptime,
                "memory_mb": memory_mb,
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            self._remove_pid_file()
            return {
                "running": False,
                "pid": None,
                "uptime_seconds": None,
                "memory_mb": None,
            }

    def get_logs(self, lines: int = 50) -> str:
        """Get recent log entries

        Args:
            lines: Number of lines to retrieve from end of log file

        Returns:
            Log content as string
        """
        if not self.log_file.exists():
            return "No log file found"

        try:
            # Read last N lines efficiently
            with open(self.log_file, "r") as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:]
                return "".join(recent_lines)
        except Exception as e:
            return f"Error reading log file: {e}"

    def _read_pid(self) -> Optional[int]:
        """Read PID from PID file

        Returns:
            PID as integer, or None if file doesn't exist or invalid
        """
        if not self.pid_file.exists():
            return None

        try:
            with open(self.pid_file, "r") as f:
                return int(f.read().strip())
        except (ValueError, IOError):
            return None

    def _write_pid(self, pid: int):
        """Write PID to PID file

        Args:
            pid: Process ID to write
        """
        with open(self.pid_file, "w") as f:
            f.write(str(pid))

    def _remove_pid_file(self):
        """Remove PID file if it exists"""
        if self.pid_file.exists():
            self.pid_file.unlink()
