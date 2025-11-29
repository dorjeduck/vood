"""
FastAPI development server for live animation preview.

Provides live browser preview with hot-reload for Vood animations.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from vood.core.logger import get_logger
from vood.vscene import VScene
from vood.vscene.preview import PreviewRenderer
from vood.vscene.vscene_exporter import VSceneExporter
from vood.converter.converter_type import ConverterType

from .file_watcher import FileWatcher
from .module_loader import safe_reload_module
from .websocket_manager import ConnectionManager
from .export_job_manager import ExportJobManager, ExportFormat, ExportStatus

logger = get_logger()


# Request/Response models
class ExportRequest(BaseModel):
    """Request model for export operations"""

    frames: int = 60
    fps: int = 30
    width_px: Optional[int] = None
    html_interactive: bool = True  # For HTML exports: interactive controls or auto-play


class BatchExportRequest(BaseModel):
    """Request model for batch export operations (multiple formats)"""

    formats: list[str]  # e.g., ["mp4", "gif"]
    frames: int = 60
    fps: int = 30
    width_px: Optional[int] = None
    html_interactive: bool = True


class DevServer:
    """
    Development server for live animation preview.

    Watches a Python animation file, reloads it on changes, and broadcasts
    updates to connected browsers via WebSocket.
    """

    def __init__(
        self,
        file_path: Path,
        num_frames: int = 20,
        play_interval_ms: int = 100,
        port: int = 8000,
    ):
        """
        Initialize development server.

        Args:
            file_path: Path to the Python animation file to watch
            num_frames: Number of frames to generate for preview
            play_interval_ms: Playback interval in milliseconds
            port: Server port
        """
        self.file_path = file_path.resolve()
        self.num_frames = num_frames
        self.play_interval_ms = play_interval_ms
        self.port = port

        # Current scene state
        self.current_scene: Optional[VScene] = None
        self.current_error: Optional[str] = None

        # WebSocket manager
        self.connection_manager = ConnectionManager()

        # Export job manager
        self.export_manager = ExportJobManager(output_dir=self.file_path.parent / "exports")

        # File watcher (will be initialized in start())
        self.file_watcher: Optional[FileWatcher] = None

        # Event loop (will be set when server starts)
        self.loop: Optional[asyncio.AbstractEventLoop] = None

        # Create FastAPI app
        self.app = self._create_app()

    def _create_app(self) -> FastAPI:
        """
        Create and configure the FastAPI application.

        Returns:
            Configured FastAPI app
        """
        app = FastAPI(
            title="Vood Dev Server",
            description="Development server for live animation preview",
            version="0.3.0",
        )

        # Store event loop on startup
        @app.on_event("startup")
        async def startup_event():
            self.loop = asyncio.get_event_loop()

        # Setup template directory
        templates_dir = Path(__file__).parent / "templates"
        templates = Jinja2Templates(directory=str(templates_dir))

        # Root endpoint - serve preview HTML
        @app.get("/", response_class=HTMLResponse)
        async def serve_preview():
            """Serve the preview HTML page."""
            return templates.TemplateResponse(
                "preview.html",
                {
                    "request": {},  # Required by Jinja2Templates
                    "filename": self.file_path.name,
                    "port": self.port,
                },
            )

        # WebSocket endpoint for live updates
        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for live preview updates."""
            await self.connection_manager.connect(websocket)

            try:
                # Send initial preview on connection
                await self._send_current_preview()

                # Keep connection alive and wait for messages (if any)
                while True:
                    # We don't expect messages from client, but need to keep connection open
                    try:
                        await websocket.receive_text()
                    except WebSocketDisconnect:
                        break

            except WebSocketDisconnect:
                pass
            finally:
                self.connection_manager.disconnect(websocket)

        # Health check endpoint
        @app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "ok",
                "service": "vood-devserver",
                "file": str(self.file_path),
            }

        # Export endpoints
        @app.post("/export/mp4")
        async def export_mp4(request: ExportRequest):
            """Export animation as MP4 video."""
            if not self.current_scene:
                return JSONResponse(
                    {"error": "No scene loaded"}, status_code=400
                )

            job = self.export_manager.create_job(ExportFormat.MP4)

            # Start export in background
            asyncio.create_task(
                self._run_mp4_export(job.job_id, request.frames, request.fps, request.width_px)
            )

            return {"job_id": job.job_id, "status": job.status.value}

        @app.post("/export/gif")
        async def export_gif(request: ExportRequest):
            """Export animation as GIF."""
            if not self.current_scene:
                return JSONResponse(
                    {"error": "No scene loaded"}, status_code=400
                )

            job = self.export_manager.create_job(ExportFormat.GIF)

            # Start export in background
            asyncio.create_task(
                self._run_gif_export(job.job_id, request.frames, request.fps, request.width_px)
            )

            return {"job_id": job.job_id, "status": job.status.value}

        @app.post("/export/html")
        async def export_html(request: ExportRequest):
            """Export animation as HTML (interactive or animation-only)."""
            if not self.current_scene:
                return JSONResponse(
                    {"error": "No scene loaded"}, status_code=400
                )

            job = self.export_manager.create_job(ExportFormat.HTML)

            # Start export in background
            asyncio.create_task(
                self._run_html_export(
                    job.job_id,
                    request.frames,
                    request.fps,
                    request.html_interactive
                )
            )

            return {"job_id": job.job_id, "status": job.status.value}

        @app.post("/export/batch")
        async def export_batch(request: BatchExportRequest):
            """Export animation in multiple formats with frame reuse optimization."""
            if not self.current_scene:
                return JSONResponse(
                    {"error": "No scene loaded"}, status_code=400
                )

            # Create jobs for each format
            job_ids = []
            formats = []

            for format_str in request.formats:
                if format_str == "mp4":
                    job = self.export_manager.create_job(ExportFormat.MP4)
                    job_ids.append(job.job_id)
                    formats.append(("mp4", job.job_id))
                elif format_str == "gif":
                    job = self.export_manager.create_job(ExportFormat.GIF)
                    job_ids.append(job.job_id)
                    formats.append(("gif", job.job_id))
                elif format_str == "html-interactive":
                    job = self.export_manager.create_job(ExportFormat.HTML)
                    job_ids.append(job.job_id)
                    formats.append(("html-interactive", job.job_id))
                elif format_str == "html-animation":
                    job = self.export_manager.create_job(ExportFormat.HTML)
                    job_ids.append(job.job_id)
                    formats.append(("html-animation", job.job_id))

            # Start batch export in background
            asyncio.create_task(
                self._run_batch_export(
                    formats,
                    request.frames,
                    request.fps,
                    request.width_px,
                    request.html_interactive
                )
            )

            return {"job_ids": job_ids, "status": "queued"}

        @app.get("/export/status/{job_id}")
        async def export_status(job_id: str):
            """Get export job status."""
            job = self.export_manager.get_job(job_id)
            if not job:
                return JSONResponse(
                    {"error": "Job not found"}, status_code=404
                )
            return job.to_dict()

        @app.post("/export/cancel/{job_id}")
        async def export_cancel(job_id: str):
            """Cancel an export job."""
            success = self.export_manager.cancel_job(job_id)
            if not success:
                return JSONResponse(
                    {"error": "Job not found or already complete"}, status_code=400
                )
            return {"status": "cancelled"}

        @app.get("/export/download/{filename}")
        async def export_download(filename: str):
            """Download exported file."""
            file_path = self.export_manager.output_dir / filename
            if not file_path.exists():
                return JSONResponse(
                    {"error": "File not found"}, status_code=404
                )
            return FileResponse(
                file_path,
                filename=filename,
                media_type="application/octet-stream",
            )

        return app

    def _generate_preview_html(self, scene: VScene) -> str:
        """
        Generate preview HTML from a VScene.

        Uses the preview renderer to create self-contained HTML.

        Args:
            scene: The VScene to render

        Returns:
            HTML string containing the interactive preview
        """
        preview_renderer = PreviewRenderer(scene)

        # Generate times for frames
        times = [i / (self.num_frames - 1) for i in range(self.num_frames)]

        # Use _render_navigator to get the HTML object
        html_obj = preview_renderer._render_navigator(
            times=times, play_interval_ms=self.play_interval_ms
        )

        # Extract HTML string from IPython.display.HTML object
        return html_obj.data

    async def _send_current_preview(self):
        """
        Send the current preview state to all connected clients.

        Sends either a preview update or error message depending on current state.
        """
        if self.current_error:
            await self.connection_manager.send_error(self.current_error)
        elif self.current_scene:
            try:
                html = self._generate_preview_html(self.current_scene)
                await self.connection_manager.send_update(html, self.num_frames)
            except Exception as e:
                error_msg = f"Error generating preview: {str(e)}"
                logger.error(error_msg)
                await self.connection_manager.send_error(error_msg)

    async def _run_mp4_export(
        self, job_id: str, total_frames: int, fps: int, width_px: Optional[int]
    ):
        """Run MP4 export in background."""
        try:
            from datetime import datetime

            exporter = VSceneExporter(
                scene=self.current_scene,
                output_dir=str(self.export_manager.output_dir),
                converter=ConverterType.PLAYWRIGHT,
            )

            def progress_callback(frame_num: int, total: int):
                """Update progress during frame generation."""
                progress = frame_num / total
                self.export_manager.update_job(
                    job_id,
                    progress=progress,
                    message=f"Generating frames {frame_num}/{total}"
                )

            def export_func():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                return exporter.to_mp4(
                    filename=f"animation_{timestamp}",
                    total_frames=total_frames,
                    framerate=fps,
                    png_width_px=width_px,
                    progress_callback=progress_callback,
                )

            await self.export_manager.run_export_job(job_id, export_func)

        except Exception as e:
            logger.error(f"MP4 export failed: {e}")
            self.export_manager.update_job(job_id, error=str(e))

    async def _run_gif_export(
        self, job_id: str, total_frames: int, fps: int, width_px: Optional[int]
    ):
        """Run GIF export in background."""
        try:
            from datetime import datetime

            exporter = VSceneExporter(
                scene=self.current_scene,
                output_dir=str(self.export_manager.output_dir),
                converter=ConverterType.PLAYWRIGHT,
            )

            def progress_callback(frame_num: int, total: int):
                """Update progress during frame generation."""
                progress = frame_num / total
                self.export_manager.update_job(
                    job_id,
                    progress=progress,
                    message=f"Generating frames {frame_num}/{total}"
                )

            def export_func():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                return exporter.to_gif(
                    filename=f"animation_{timestamp}",
                    total_frames=total_frames,
                    framerate=fps,
                    png_width_px=width_px,
                    progress_callback=progress_callback,
                )

            await self.export_manager.run_export_job(job_id, export_func)

        except Exception as e:
            logger.error(f"GIF export failed: {e}")
            self.export_manager.update_job(job_id, error=str(e))

    async def _run_html_export(
        self, job_id: str, total_frames: int, fps: int, interactive: bool = True
    ):
        """Run HTML export in background."""
        try:
            from datetime import datetime

            exporter = VSceneExporter(
                scene=self.current_scene,
                output_dir=str(self.export_manager.output_dir),
            )

            def export_func():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                return exporter.to_html(
                    filename=f"animation_{timestamp}",
                    total_frames=total_frames,
                    framerate=fps,
                    interactive=interactive,
                )

            await self.export_manager.run_export_job(job_id, export_func)

        except Exception as e:
            logger.error(f"HTML export failed: {e}")
            self.export_manager.update_job(job_id, error=str(e))

    async def _run_batch_export(
        self,
        formats: list[tuple[str, str]],  # [(format_name, job_id), ...]
        total_frames: int,
        fps: int,
        width_px: Optional[int],
        html_interactive: bool = True,
    ):
        """Run batch export with frame reuse optimization."""
        import tempfile
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        frames_dir = None
        temp_context = None

        try:
            # Update all jobs to processing
            for _, job_id in formats:
                self.export_manager.update_job(
                    job_id,
                    status=ExportStatus.PROCESSING,
                    message="Starting batch export..."
                )

            # Create shared temporary directory for frames
            temp_context = tempfile.TemporaryDirectory(prefix="vood_batch_frames_")
            frames_dir = Path(temp_context.name)

            logger.info(f"Generating {total_frames} frames once for {len(formats)} format(s)...")

            # Generate PNG frames once
            exporter = VSceneExporter(
                scene=self.current_scene,
                output_dir=str(self.export_manager.output_dir),
                converter=ConverterType.PLAYWRIGHT,
            )

            def progress_callback(frame_num: int, total: int):
                """Update progress for all jobs during frame generation."""
                progress = (frame_num / total) * 0.5  # Frame generation is 50% of total
                for _, job_id in formats:
                    self.export_manager.update_job(
                        job_id,
                        progress=progress,
                        message=f"Generating frames {frame_num}/{total}"
                    )

            # Generate frames
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._generate_frames_for_batch,
                exporter,
                frames_dir,
                total_frames,
                fps,
                width_px,
                progress_callback
            )

            # Create each format from the shared frames
            for idx, (format_name, job_id) in enumerate(formats):
                format_progress_start = 0.5 + (idx / len(formats)) * 0.5
                format_progress_end = 0.5 + ((idx + 1) / len(formats)) * 0.5

                try:
                    if format_name == "mp4":
                        await self._create_mp4_from_frames(
                            job_id, frames_dir, total_frames, fps, timestamp,
                            format_progress_start, format_progress_end
                        )
                    elif format_name == "gif":
                        await self._create_gif_from_frames(
                            job_id, frames_dir, total_frames, fps, timestamp,
                            format_progress_start, format_progress_end
                        )
                    elif format_name in ["html-interactive", "html-animation"]:
                        interactive = (format_name == "html-interactive")
                        await loop.run_in_executor(
                            None,
                            self._create_html_export,
                            job_id, total_frames, fps, interactive, timestamp
                        )
                        self.export_manager.update_job(
                            job_id,
                            status=ExportStatus.COMPLETE,
                            progress=1.0,
                            message="Export complete"
                        )
                except Exception as e:
                    logger.error(f"{format_name.upper()} export failed: {e}")
                    self.export_manager.update_job(job_id, error=str(e))

        except Exception as e:
            logger.error(f"Batch export failed: {e}")
            for _, job_id in formats:
                job = self.export_manager.get_job(job_id)
                if job and job.status == ExportStatus.PROCESSING:
                    self.export_manager.update_job(job_id, error=str(e))

        finally:
            # Cleanup temporary directory
            if temp_context:
                temp_context.cleanup()

    def _generate_frames_for_batch(
        self,
        exporter: VSceneExporter,
        frames_dir: Path,
        total_frames: int,
        fps: int,
        width_px: Optional[int],
        progress_callback: callable,
    ):
        """Generate PNG frames for batch export (runs in thread pool)."""
        for frame_num, t in exporter.to_frames(
            output_dir=str(frames_dir),
            filename_pattern="frame_{:04d}",
            total_frames=total_frames,
            format="png",
            png_width_px=width_px,
            cleanup_svg_after_png_conversion=True,
            progress_callback=progress_callback,
        ):
            pass  # Frames are generated, progress is tracked

    async def _create_mp4_from_frames(
        self,
        job_id: str,
        frames_dir: Path,
        total_frames: int,
        fps: int,
        timestamp: str,
        progress_start: float,
        progress_end: float,
    ):
        """Create MP4 from existing PNG frames."""
        from datetime import datetime
        import subprocess

        self.export_manager.update_job(
            job_id,
            progress=progress_start,
            message="Encoding MP4..."
        )

        output_path = self.export_manager.output_dir / f"animation_{timestamp}.mp4"

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self._encode_mp4,
            frames_dir,
            output_path,
            fps
        )

        self.export_manager.update_job(
            job_id,
            status=ExportStatus.COMPLETE,
            progress=1.0,
            output_file=output_path,
            message="Export complete"
        )

    def _encode_mp4(self, frames_dir: Path, output_path: Path, fps: int):
        """Encode MP4 from frames using ffmpeg (runs in thread pool)."""
        import subprocess

        cmd = [
            "ffmpeg",
            "-y",
            "-framerate", str(fps),
            "-i", str(frames_dir / "frame_%04d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            str(output_path)
        ]

        subprocess.run(cmd, check=True, capture_output=True)

    async def _create_gif_from_frames(
        self,
        job_id: str,
        frames_dir: Path,
        total_frames: int,
        fps: int,
        timestamp: str,
        progress_start: float,
        progress_end: float,
    ):
        """Create GIF from existing PNG frames."""
        try:
            from PIL import Image
        except ImportError:
            raise RuntimeError("Pillow required for GIF export")

        self.export_manager.update_job(
            job_id,
            progress=progress_start,
            message="Creating GIF..."
        )

        output_path = self.export_manager.output_dir / f"animation_{timestamp}.gif"

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self._encode_gif,
            frames_dir,
            output_path,
            total_frames,
            fps
        )

        self.export_manager.update_job(
            job_id,
            status=ExportStatus.COMPLETE,
            progress=1.0,
            output_file=output_path,
            message="Export complete"
        )

    def _encode_gif(self, frames_dir: Path, output_path: Path, total_frames: int, fps: int):
        """Encode GIF from frames using Pillow (runs in thread pool)."""
        from PIL import Image

        frames = []
        for i in range(total_frames):
            frame_path = frames_dir / f"frame_{i:04d}.png"
            if frame_path.exists():
                frames.append(Image.open(frame_path))

        duration_ms = int(1000 / fps)
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration_ms,
            loop=0,
            optimize=True,
        )

    def _create_html_export(
        self,
        job_id: str,
        total_frames: int,
        fps: int,
        interactive: bool,
        timestamp: str,
    ):
        """Create HTML export (runs in thread pool)."""
        exporter = VSceneExporter(
            scene=self.current_scene,
            output_dir=str(self.export_manager.output_dir),
        )

        output_file = exporter.to_html(
            filename=f"animation_{timestamp}",
            total_frames=total_frames,
            framerate=fps,
            interactive=interactive,
        )

        self.export_manager.update_job(
            job_id,
            output_file=Path(output_file)
        )

    def _on_file_changed(self):
        """
        Callback invoked when the animation file changes.

        Reloads the module and broadcasts the update to all clients.
        This runs in the file watcher thread, so we need to schedule
        the async task in the main event loop.
        """
        logger.info(f"File changed: {self.file_path.name}")

        # Reload module
        scene, error = safe_reload_module(self.file_path)

        if error:
            logger.error(f"Reload error: {error}")
            self.current_scene = None
            self.current_error = error
        else:
            logger.info(f"Reload successful: {self.file_path.name}")
            self.current_scene = scene
            self.current_error = None

        # Schedule the async task in the main event loop
        # (file watcher runs in a different thread)
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._send_current_preview(), self.loop
            )

    def start_watching(self):
        """
        Start watching the animation file for changes.

        Also performs initial module load.
        """
        # Initial load
        logger.info(f"Loading animation file: {self.file_path}")
        scene, error = safe_reload_module(self.file_path)

        if error:
            logger.error(f"Initial load error: {error}")
            self.current_error = error
        else:
            logger.info(f"Initial load successful: {self.file_path.name}")
            self.current_scene = scene

        # Start file watcher
        self.file_watcher = FileWatcher(
            file_path=self.file_path,
            on_change_callback=self._on_file_changed,
            debounce_ms=200,
        )
        self.file_watcher.start()
        logger.info(f"Watching for changes: {self.file_path}")

    def stop_watching(self):
        """Stop watching the animation file."""
        if self.file_watcher:
            self.file_watcher.stop()
            logger.info("File watching stopped")


def create_app(
    file_path: Path,
    num_frames: int = 20,
    play_interval_ms: int = 100,
    port: int = 8000,
) -> tuple[FastAPI, DevServer]:
    """
    Create a development server app.

    Args:
        file_path: Path to the Python animation file
        num_frames: Number of frames for preview
        play_interval_ms: Playback interval in milliseconds
        port: Server port

    Returns:
        Tuple of (FastAPI app, DevServer instance)
    """
    dev_server = DevServer(
        file_path=file_path,
        num_frames=num_frames,
        play_interval_ms=play_interval_ms,
        port=port,
    )

    return dev_server.app, dev_server
