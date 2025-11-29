"""Unified exporter for VScene - handles static and animated exports"""

from __future__ import annotations

from typing import Optional, Callable
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
import shutil
import subprocess
import tempfile

from vood.converter.converter_type import ConverterType
from vood.core.logger import get_logger

logger = get_logger()


@dataclass
class ExportResult:
    """Result of an export operation"""

    success: bool
    files: dict[str, str]  # format -> file path
    error: Optional[str] = None


class VSceneExporter:
    """Unified exporter for VScene supporting static and animated exports.

    Handles:
    - Static exports: SVG, PNG, PDF at specific time points
    - Animation exports: Frame sequences and video files
    """

    # Constants
    DEFAULT_FRAME_PATTERN = "frame_{:04d}"
    DEFAULT_FRAMERATE = 30
    DEFAULT_CODEC = "libx264"
    SUPPORTED_FORMATS = {"svg", "png", "pdf"}
    SUPPORTED_VIDEO_CODECS = {"libx264", "libx265", "vp9"}

    def __init__(
        self,
        scene,
        output_dir: Optional[str] = ".",
        converter: ConverterType = ConverterType.PLAYWRIGHT,
        timestamp_files: bool = False,
    ) -> None:
        """Initialize exporter

        Args:
            scene: The VScene to export
            output_dir: Directory to save exported files
            converter: ConverterType enum for PNG/PDF conversion
            timestamp_files: Whether to prefix filenames with timestamps
        """
        self.scene = scene
        self.output_dir = (
            Path(output_dir) if not isinstance(output_dir, Path) else output_dir
        )
        self.timestamp_files = timestamp_files
        self.converter = self._init_converter(converter)

    # ========================================================================
    # INITIALIZATION & VALIDATION
    # ========================================================================

    def _init_converter(self, converter: ConverterType):
        """Initialize converter instance based on type"""
        # Lazy imports to avoid importing optional dependencies at module load time
        from vood.converter.cairo_svg_converter import CairoSvgConverter
        from vood.converter.inkscape_svg_converter import InkscapeSvgConverter
        from vood.converter.playwright_svg_converter import PlaywrightSvgConverter
        from vood.converter.playwright_http_svg_converter import PlaywrightHttpSvgConverter

        converter_map = {
            ConverterType.CAIROSVG: CairoSvgConverter,
            ConverterType.INKSCAPE: InkscapeSvgConverter,
            ConverterType.PLAYWRIGHT: PlaywrightSvgConverter,
            ConverterType.PLAYWRIGHT_HTTP: PlaywrightHttpSvgConverter,
        }

        converter_class = converter_map.get(converter)
        if converter_class:
            return converter_class()

        logger.warning(f"Unrecognized converter '{converter}', defaulting to CairoSVG")
        return CairoSvgConverter()

    def _validate_formats(self, formats: list[str]) -> None:
        """Validate that requested formats are supported"""
        invalid = set(formats) - self.SUPPORTED_FORMATS
        if invalid:
            raise ValueError(
                f"Unsupported formats: {invalid}. Supported: {self.SUPPORTED_FORMATS}"
            )

    def _validate_video_params(
        self, total_frames: int, framerate: int, num_thumbnails: int, codec: str
    ) -> None:
        """Validate video export parameters"""
        if total_frames < 1:
            raise ValueError(f"total_frames must be >= 1, got {total_frames}")
        if framerate < 1:
            raise ValueError(f"framerate must be >= 1, got {framerate}")
        if num_thumbnails < 0:
            raise ValueError(f"num_thumbnails must be >= 0, got {num_thumbnails}")
        if codec not in self.SUPPORTED_VIDEO_CODECS:
            logger.warning(
                f"Codec '{codec}' not in known codecs {self.SUPPORTED_VIDEO_CODECS}"
            )

    def _validate_dimensions(
        self,
        png_width_px: Optional[int],
        png_height_px: Optional[int],
        pdf_inch_width: Optional[float],
        pdf_inch_height: Optional[float],
    ) -> None:
        """Validate dimension parameters"""
        if png_width_px is not None and png_width_px < 1:
            raise ValueError(f"png_width_px must be >= 1, got {png_width_px}")
        if png_height_px is not None and png_height_px < 1:
            raise ValueError(f"png_height_px must be >= 1, got {png_height_px}")
        if pdf_inch_width is not None and pdf_inch_width <= 0:
            raise ValueError(f"pdf_inch_width must be > 0, got {pdf_inch_width}")
        if pdf_inch_height is not None and pdf_inch_height <= 0:
            raise ValueError(f"pdf_inch_height must be > 0, got {pdf_inch_height}")

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _generate_output_path(self, filename: str, extension: str = None) -> Path:
        """Generate output path with optional timestamp

        Args:
            filename: Base filename (can include extension)
            extension: Override extension (e.g., ".mp4")

        Returns:
            Full output path
        """
        path = Path(filename)

        if self.timestamp_files:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stem = f"{path.stem}_{timestamp}"
        else:
            stem = path.stem

        # Use provided extension or original
        ext = extension if extension else path.suffix
        if not ext.startswith(".") and len(ext) > 0:
            ext = f".{ext}"

        output_path = self.output_dir / f"{stem}{ext}"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        return output_path

    def _needs_converter(self, formats: list[str]) -> list[str]:
        """Get formats that require converter (non-SVG)"""
        return [fmt for fmt in formats if fmt != "svg"]

    def _calculate_frame_time(
        self,
        frame_num: int,
        total_frames: int,
        easing: Optional[Callable[[float], float]] = None,
    ) -> float:
        """Calculate normalized time for a frame number

        Args:
            frame_num: Current frame number (0-indexed)
            total_frames: Total number of frames
            easing: Optional easing function to apply

        Returns:
            Time value between 0.0 and 1.0
        """
        t = frame_num / (total_frames - 1) if total_frames > 1 else 0.0
        return easing(t) if easing else t

    def _infer_formats_from_extension(self, extension: str) -> list[str]:
        """Infer export formats from file extension"""
        ext = extension.lower().lstrip(".")

        if ext == "svg":
            return ["svg"]
        elif ext == "png":
            return ["png"]
        elif ext == "pdf":
            return ["pdf"]
        else:
            raise ValueError(
                f"Unsupported file extension '.{ext}'. "
                f"Use one of: {', '.join(f'.{fmt}' for fmt in self.SUPPORTED_FORMATS)}"
            )

    def _log_progress(self, frame_num: int, total_frames: int, step: int = 10) -> None:
        """Log frame generation progress"""
        if frame_num % max(1, total_frames // step) == 0:
            progress = (frame_num / total_frames) * 100
            logger.info(
                f"Frame generation progress: {progress:.0f}% ({frame_num}/{total_frames})"
            )

    # ========================================================================
    # STATIC EXPORTS
    # ========================================================================

    def export(
        self,
        filename: str,
        frame_time: float = 0.0,
        formats: Optional[list[str]] = None,
        png_width_px: Optional[int] = None,
        png_height_px: Optional[int] = None,
        png_thumbnail_width_px: Optional[int] = None,
        png_thumbnail_height_px: Optional[int] = None,
        pdf_inch_width: Optional[float] = None,
        pdf_inch_height: Optional[float] = None,
    ) -> ExportResult:
        """Export scene at specific time point to various formats.

        Args:
            filename: Output filename (extension determines default format)
            frame_time: Time point to render (0.0 to 1.0)
            formats: List of formats to export (e.g. ["png", "pdf", "svg"])
            png_width_px: Width in pixels for PNG export
            png_height_px: Height in pixels for PNG export
            png_thumbnail_width_px: Width for PNG thumbnail
            png_thumbnail_height_px: Height for PNG thumbnail
            pdf_inch_width: Width in inches for PDF export
            pdf_inch_height: Height in inches for PDF export

        Returns:
            ExportResult with paths to exported files
        """
        # Validate frame_time
        if not 0.0 <= frame_time <= 1.0:
            raise ValueError(
                f"frame_time must be between 0.0 and 1.0, got {frame_time}"
            )

        # Infer formats from extension if not specified
        path = Path(filename)
        if formats is None:
            try:
                formats = self._infer_formats_from_extension(path.suffix)
            except ValueError as e:
                return ExportResult(success=False, files={}, error=str(e))

        # Validate formats and dimensions
        try:
            self._validate_formats(formats)
            self._validate_dimensions(
                png_width_px, png_height_px, pdf_inch_width, pdf_inch_height
            )
        except ValueError as e:
            return ExportResult(success=False, files={}, error=str(e))

        files = {}

        # Handle SVG export (native)
        if "svg" in formats:
            svg_path = self._generate_output_path(filename, ".svg")
            self.scene.to_svg(filename=str(svg_path), frame_time=frame_time)
            logger.info(f'SVG exported to "{svg_path}"')
            files["svg"] = str(svg_path)

        # Handle PNG/PDF exports (via converter)
        converter_formats = self._needs_converter(formats)
        if converter_formats:
            output_path = self._generate_output_path(filename)

            conv_results = self.converter.convert(
                self.scene,
                str(output_path),
                frame_time=frame_time,
                formats=converter_formats,
                png_width_px=png_width_px,
                png_height_px=png_height_px,
                png_thumb_width_px=png_thumbnail_width_px,
                png_thumb_height_px=png_thumbnail_height_px,
                pdf_inch_width=pdf_inch_width,
                pdf_inch_height=pdf_inch_height,
            )

            if conv_results:
                files.update(conv_results)
                for fmt, path in conv_results.items():
                    logger.info(f'{fmt.upper()} exported to "{path}"')

        return ExportResult(success=True, files=files)

    def to_png(
        self,
        filename: str,
        frame_time: float = 0.0,
        png_width_px: Optional[int] = None,
        png_height_px: Optional[int] = None,
    ) -> str:
        """Export scene to PNG at specific time point.

        Convenience method for PNG-only export.

        Args:
            filename: Output filename
            frame_time: Time point to render (0.0 to 1.0)
            png_width_px: Width in pixels
            png_height_px: Height in pixels

        Returns:
            Path to exported PNG file
        """
        result = self.export(
            filename,
            frame_time=frame_time,
            formats=["png"],
            png_width_px=png_width_px,
            png_height_px=png_height_px,
        )

        if not result.success:
            raise RuntimeError(f"PNG export failed: {result.error}")

        return result.files.get("png")

    def to_pdf(
        self,
        filename: str,
        frame_time: float = 0.0,
        pdf_inch_width: Optional[float] = None,
        pdf_inch_height: Optional[float] = None,
    ) -> str:
        """Export scene to PDF at specific time point.

        Convenience method for PDF-only export.

        Args:
            filename: Output filename
            frame_time: Time point to render (0.0 to 1.0)
            pdf_inch_width: Width in inches
            pdf_inch_height: Height in inches

        Returns:
            Path to exported PDF file
        """
        result = self.export(
            filename,
            frame_time=frame_time,
            formats=["pdf"],
            pdf_inch_width=pdf_inch_width,
            pdf_inch_height=pdf_inch_height,
        )

        if not result.success:
            raise RuntimeError(f"PDF export failed: {result.error}")

        return result.files.get("pdf")

    # ========================================================================
    # ANIMATION EXPORTS
    # ========================================================================

    def to_gif(
        self,
        filename: str,
        total_frames: int = 60,
        framerate: int = DEFAULT_FRAMERATE,
        easing: Optional[Callable[[float], float]] = None,
        png_width_px: Optional[int] = None,
        png_height_px: Optional[int] = None,
        loop: int = 0,
        optimize: bool = True,
        cleanup_intermediate_files: bool = True,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> str:
        """Export scene as animated GIF file.

        Args:
            filename: Output GIF filename (without extension)
            total_frames: Number of frames to generate
            framerate: Animation framerate (fps)
            easing: Optional easing function
            png_width_px: Width for frames
            png_height_px: Height for frames
            loop: Number of loops (0 = infinite)
            optimize: Optimize GIF file size
            cleanup_intermediate_files: Whether to delete frame images after encoding
            progress_callback: Optional callback(frame_num, total_frames) for progress tracking

        Returns:
            Path to the exported GIF file
        """
        try:
            from PIL import Image
        except ImportError:
            raise RuntimeError(
                "Pillow (PIL) is required for GIF export. Install with: pip install Pillow"
            )

        # Validation
        if total_frames < 1:
            raise ValueError(f"total_frames must be >= 1, got {total_frames}")
        if framerate < 1:
            raise ValueError(f"framerate must be >= 1, got {framerate}")

        # Setup output path
        output_path = self._generate_output_path(filename, ".gif")
        base_name = output_path.stem

        # Setup frame directory
        if cleanup_intermediate_files:
            # Use temporary directory
            temp_context = tempfile.TemporaryDirectory(prefix="vood_gif_frames_")
            frames_dir = Path(temp_context.name)
        else:
            # Use persistent directory
            frames_dir = self.output_dir / f"{base_name}_frames"
            frames_dir.mkdir(parents=True, exist_ok=True)
            temp_context = None

        try:
            # Generate PNG frames
            logger.info(f"Generating {total_frames} frames for GIF...")

            for frame_num, t in self.to_frames(
                output_dir=str(frames_dir),
                filename_pattern=self.DEFAULT_FRAME_PATTERN,
                total_frames=total_frames,
                format="png",
                easing=easing,
                png_width_px=png_width_px,
                png_height_px=png_height_px,
                cleanup_svg_after_png_conversion=True,
                progress_callback=progress_callback,
            ):
                pass

            # Load all frames
            logger.info("Creating GIF from frames...")
            frames = []
            for i in range(total_frames):
                frame_path = frames_dir / f"frame_{i:04d}.png"
                if frame_path.exists():
                    frames.append(Image.open(frame_path))
                else:
                    logger.warning(f"Frame {frame_path} not found")

            if not frames:
                raise RuntimeError("No frames were generated")

            # Calculate duration per frame in milliseconds
            duration_ms = int(1000 / framerate)

            # Save as GIF
            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                duration=duration_ms,
                loop=loop,
                optimize=optimize,
            )

            # Close all image handles
            for frame in frames:
                frame.close()

        finally:
            # Cleanup temporary directory if it exists
            if temp_context:
                temp_context.cleanup()

        logger.info(f'GIF exported to "{output_path}"')
        return str(output_path)

    def to_html(
        self,
        filename: str,
        total_frames: int = 60,
        framerate: int = DEFAULT_FRAMERATE,
        interactive: bool = True,
    ) -> str:
        """Export scene as self-contained HTML file.

        Creates a single HTML file with embedded SVG frames and JavaScript.
        Perfect for embedding animations in websites - no external dependencies.

        Args:
            filename: Output HTML filename (without extension)
            total_frames: Number of frames to generate
            framerate: Playback framerate (fps)
            interactive: If True, includes controls (play/pause, slider).
                        If False, creates auto-playing looping animation.

        Returns:
            Path to the exported HTML file
        """
        from vood.vscene.preview import PreviewRenderer

        # Validation
        if total_frames < 2:
            raise ValueError(f"total_frames must be >= 2, got {total_frames}")
        if framerate < 1:
            raise ValueError(f"framerate must be >= 1, got {framerate}")

        # Setup output path
        output_path = self._generate_output_path(filename, ".html")

        # Generate times for frames
        times = [i / (total_frames - 1) for i in range(total_frames)]

        # Calculate play interval from framerate
        play_interval_ms = int(1000 / framerate)

        # Generate HTML based on mode
        if interactive:
            logger.info(f"Generating interactive HTML with {total_frames} frames...")
            preview_renderer = PreviewRenderer(self.scene)
            html_obj = preview_renderer._render_navigator(
                times=times, play_interval_ms=play_interval_ms
            )
            html_content = html_obj.data
        else:
            logger.info(f"Generating animation-only HTML with {total_frames} frames...")
            html_content = self._generate_animation_html(times, play_interval_ms)

        # Wrap in complete HTML document
        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vood Animation</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: #f5f5f5;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
"""

        # Write to file
        output_path.write_text(full_html, encoding="utf-8")
        logger.info(f'HTML exported to "{output_path}"')
        return str(output_path)

    def _generate_animation_html(self, times: list[float], play_interval_ms: int) -> str:
        """Generate simple auto-playing animation HTML without controls.

        Args:
            times: List of time points to render
            play_interval_ms: Milliseconds between frames

        Returns:
            HTML string with embedded SVG frames and auto-play script
        """
        import uuid

        preview_id = str(uuid.uuid4())[:8]
        num_frames = len(times)

        # Generate all SVG frames
        frames_html = []
        for i, t in enumerate(times):
            svg = self.scene.to_svg(frame_time=t, log=False)
            active = 'active' if i == 0 else ''
            frames_html.append(f'''
                <div class="frame-{preview_id} {active}" id="frame-{preview_id}-{i}">
                    {svg}
                </div>
            ''')

        # Build complete HTML with minimal styling and auto-play
        html = f'''
            <style>
                .animation-container-{preview_id} {{
                    display: inline-block;
                }}
                .frame-{preview_id} {{
                    display: none;
                }}
                .frame-{preview_id}.active {{
                    display: block;
                }}
            </style>
            <div class="animation-container-{preview_id}">
                {''.join(frames_html)}
            </div>
            <script>
                (function() {{
                    let currentFrame = 0;
                    const totalFrames = {num_frames};
                    const interval = {play_interval_ms};

                    function showFrame(index) {{
                        const frames = document.querySelectorAll('.frame-{preview_id}');
                        frames.forEach(f => f.classList.remove('active'));
                        if (frames[index]) {{
                            frames[index].classList.add('active');
                        }}
                    }}

                    function nextFrame() {{
                        currentFrame = (currentFrame + 1) % totalFrames;
                        showFrame(currentFrame);
                    }}

                    // Auto-start animation
                    setInterval(nextFrame, interval);
                }})();
            </script>
        '''

        return html

    def to_frames(
        self,
        output_dir: str,
        filename_pattern: str = DEFAULT_FRAME_PATTERN,
        total_frames: int = 60,
        format: str = "svg",
        easing: Optional[Callable[[float], float]] = None,
        png_width_px: Optional[int] = None,
        png_height_px: Optional[int] = None,
        cleanup_svg_after_png_conversion: bool = True,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ):
        """Export animation as frame sequence.

        Args:
            output_dir: Directory to save frames
            filename_pattern: Pattern for frame filenames (must include format placeholder like {:04d})
            total_frames: Number of frames to generate
            format: Format for frames ("svg", "png", or "pdf")
            easing: Optional easing function for animation
            png_width_px: Width for PNG frames
            png_height_px: Height for PNG frames
            cleanup_svg_after_png_conversion: If format is PNG, whether to delete intermediate SVG files
            progress_callback: Optional callback(frame_num, total_frames) for progress tracking

        Yields:
            Tuple of (frame_num, frame_time) for progress tracking
        """
        # Validation
        if total_frames < 1:
            raise ValueError(f"total_frames must be >= 1, got {total_frames}")
        if format not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"format must be one of {self.SUPPORTED_FORMATS}, got '{format}'"
            )
        if "{" not in filename_pattern:
            raise ValueError(
                f"filename_pattern must include format placeholder like {{:04d}}"
            )

        frames_dir = Path(output_dir)
        frames_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Generating {total_frames} frames in {format} format...")

        # Track intermediate files for cleanup
        svg_files = []

        for frame_num in range(total_frames):
            # Calculate frame time

            t = self._calculate_frame_time(frame_num, total_frames, easing)

            # Progress tracking
            if progress_callback:
                progress_callback(frame_num, total_frames)
            else:
                self._log_progress(frame_num, total_frames)

            filename = filename_pattern.format(frame_num)

            if format == "svg":
                # Direct SVG export
                output_file = frames_dir / f"{filename}.svg"
                self.scene.to_svg(filename=str(output_file), frame_time=t, log=False)

            elif format == "png":
                # Export SVG first if cleanup is needed
                if cleanup_svg_after_png_conversion:
                    svg_file = frames_dir / f"{filename}.svg"
                    self.scene.to_svg(filename=str(svg_file), frame_time=t, log=False)
                    svg_files.append(svg_file)

                # Convert to PNG
                png_file = frames_dir / f"{filename}.png"
                self.converter.convert(
                    self.scene,
                    str(png_file),
                    frame_time=t,
                    formats=["png"],
                    png_width_px=png_width_px,
                    png_height_px=png_height_px,
                )

            elif format == "pdf":
                output_file = frames_dir / f"{filename}.pdf"
                self.converter.convert(
                    self.scene,
                    str(output_file),
                    frame_time=t,
                    formats=["pdf"],
                )

            yield frame_num, t

        # Cleanup intermediate SVG files if requested
        if format == "png" and cleanup_svg_after_png_conversion and svg_files:
            logger.debug(f"Cleaning up {len(svg_files)} intermediate SVG files...")
            for svg_file in svg_files:
                try:
                    svg_file.unlink()
                except OSError as e:
                    logger.warning(f"Failed to delete {svg_file}: {e}")

        logger.info(f"Frame generation complete: {total_frames} frames in {frames_dir}")

    def to_mp4(
        self,
        filename: str,
        total_frames: int = 60,
        framerate: int = DEFAULT_FRAMERATE,
        easing: Optional[Callable[[float], float]] = None,
        png_width_px: Optional[int] = None,
        png_height_px: Optional[int] = None,
        cleanup_intermediate_files: bool = True,
        codec: str = DEFAULT_CODEC,
        num_thumbnails: int = 0,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> str:
        """Export scene as MP4 video file, with optional thumbnail generation.

        Args:
            filename: Output video filename (without extension)
            total_frames: Number of frames to generate
            framerate: Video framerate (fps)
            easing: Optional easing function
            png_width_px: Width for video frames
            png_height_px: Height for video frames
            cleanup_intermediate_files: Whether to delete frame images after encoding
            codec: Video codec (default: libx264 for MP4)
            num_thumbnails: Number of thumbnails to generate (0 = none, 1 = middle, 2 = start/end, etc.)
            progress_callback: Optional callback(frame_num, total_frames) for progress tracking

        Returns:
            Path to the exported video file
        """
        # Validation
        self._validate_video_params(total_frames, framerate, num_thumbnails, codec)

        if not self._check_ffmpeg_available():
            raise RuntimeError(
                "ffmpeg is required for video export but is not available"
            )

        # Setup output path
        output_path = self._generate_output_path(filename, ".mp4")
        base_name = output_path.stem

        # Setup frame directory
        if cleanup_intermediate_files:
            # Use temporary directory
            temp_context = tempfile.TemporaryDirectory(prefix="vood_frames_")
            frames_dir = Path(temp_context.name)
        else:
            # Use persistent directory
            frames_dir = self.output_dir / f"{base_name}_frames"
            frames_dir.mkdir(parents=True, exist_ok=True)
            temp_context = None

        try:
            # Generate PNG frames
            logger.info(f"Generating {total_frames} frames for video...")

            frame_times = []  # Track for thumbnail generation
            for frame_num, t in self.to_frames(
                output_dir=str(frames_dir),
                filename_pattern=self.DEFAULT_FRAME_PATTERN,
                total_frames=total_frames,
                format="png",
                easing=easing,
                png_width_px=png_width_px,
                png_height_px=png_height_px,
                cleanup_svg_after_png_conversion=False,  # Keep frames for ffmpeg
                progress_callback=progress_callback,
            ):
                frame_times.append(t)

            # Create video with ffmpeg
            logger.info("Encoding video with ffmpeg...")
            self._create_video_from_pngs(frames_dir, output_path, framerate, codec)

            # Generate thumbnails if requested
            if num_thumbnails > 0:
                self._generate_thumbnails(
                    frames_dir, base_name, total_frames, num_thumbnails
                )

        finally:
            # Cleanup temporary directory if it exists
            if temp_context:
                temp_context.cleanup()

        logger.info(f'Video exported to "{output_path}"')
        return str(output_path)

    def _generate_thumbnails(
        self,
        frames_dir: Path,
        base_name: str,
        total_frames: int,
        num_thumbnails: int,
    ) -> None:
        """Generate thumbnails from frame sequence

        Args:
            frames_dir: Directory containing frame PNG files
            base_name: Base name for thumbnail directory
            total_frames: Total number of frames
            num_thumbnails: Number of thumbnails to generate
        """
        # Calculate thumbnail indices
        if num_thumbnails == 1:
            thumbnail_indices = [total_frames // 2]
        else:
            # Evenly spaced: start, end, and in between
            thumbnail_indices = [
                int(i * (total_frames - 1) / (num_thumbnails - 1))
                for i in range(num_thumbnails)
            ]

        # Create thumbnail directory
        thumb_dir = self.output_dir / f"{base_name}_thumbnails"
        thumb_dir.mkdir(parents=True, exist_ok=True)

        # Copy thumbnail frames
        copied_count = 0
        for idx in thumbnail_indices:
            src = frames_dir / f"frame_{idx:04d}.png"
            dst = thumb_dir / f"thumbnail_{idx:04d}.png"

            if src.exists():
                try:
                    shutil.copy(src, dst)
                    copied_count += 1
                except OSError as e:
                    logger.warning(f"Failed to copy thumbnail {src}: {e}")
            else:
                logger.warning(f"Frame {src} not found for thumbnail")

        if copied_count > 0:
            logger.info(f"{copied_count} thumbnails saved to {thumb_dir}")
        else:
            logger.warning("No thumbnails were generated")

    def _create_video_from_pngs(
        self,
        png_dir: Path,
        output_path: Path,
        framerate: int,
        codec: str,
    ) -> None:
        """Create video from PNG frames using ffmpeg

        Args:
            png_dir: Directory containing PNG frames
            output_path: Output video file path
            framerate: Video framerate
            codec: Video codec to use
        """
        input_pattern = str(png_dir / "frame_%04d.png")

        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output file
            "-framerate",
            str(framerate),
            "-i",
            input_pattern,
            "-c:v",
            codec,
            "-pix_fmt",
            "yuv420p",  # Compatibility
            str(output_path),
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=300,  # 5 minute timeout
            )
            logger.debug("Video encoding complete")

        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg failed with return code {e.returncode}")
            logger.error(f"stderr: {e.stderr}")
            raise RuntimeError(f"Video encoding failed: {e.stderr}")

        except subprocess.TimeoutExpired:
            logger.error("ffmpeg timed out after 5 minutes")
            raise RuntimeError("Video encoding timed out")

        except Exception as e:
            logger.error(f"Unexpected error during video encoding: {e}")
            raise

    def _check_ffmpeg_available(self) -> bool:
        """Check if ffmpeg is available on the system

        Returns:
            True if ffmpeg is available
        """
        try:
            subprocess.run(
                ["ffmpeg", "-version"], capture_output=True, check=True, timeout=5
            )
            return True
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            return False
