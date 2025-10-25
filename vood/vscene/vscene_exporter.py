"""Unified exporter for VScene - handles static and animated exports"""

from __future__ import annotations

from typing import Optional, Callable
from datetime import datetime
from pathlib import Path
import shutil
import subprocess
import time

from vood.converter.playwright_http_svg_converter import PlaywrightHttpSvgConverter
from vood.converter.cairo_svg_converter import CairoSvgConverter
from vood.converter.inkscape_svg_converter import InkscapeSvgConverter
from vood.converter.playwright_svg_converter import PlaywrightSvgConverter
from vood.converter.converter_type import ConverterType
from vood.utils.logger import get_logger

logger = get_logger()


class VSceneExporter:
    """Unified exporter for VScene supporting static and animated exports.

    Handles:
    - Static exports: SVG, PNG, PDF at specific time points
    - Animation exports: Frame sequences and video files
    """

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

        # Initialize converter
        if converter == ConverterType.CAIROSVG:
            self.converter = CairoSvgConverter()
        elif converter == ConverterType.INKSCAPE:
            self.converter = InkscapeSvgConverter()
        elif converter == ConverterType.PLAYWRIGHT:
            self.converter = PlaywrightSvgConverter()
        elif converter == ConverterType.PLAYWRIGHT_HTTP:
            self.converter = PlaywrightHttpSvgConverter()
        else:
            logger.warning(
                f"Unrecognized converter '{converter}', defaulting to 'cairosvg'"
            )
            self.converter = CairoSvgConverter()

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
        png_thumb_width_px: Optional[int] = None,
        png_thumb_height_px: Optional[int] = None,
        pdf_inch_width: Optional[int] = None,
        pdf_inch_height: Optional[int] = None,
    ) -> dict:
        """Export scene at specific time point to various formats.

        Args:
            filename: Output filename (extension determines default format)
            frame_time: Time point to render (0.0 to 1.0)
            formats: List of formats to export (e.g. ["png", "pdf", "svg"])
            png_width_px: Width in pixels for PNG export
            png_height_px: Height in pixels for PNG export
            png_thumb_width_px: Width for PNG thumbnail
            png_thumb_height_px: Height for PNG thumbnail
            pdf_inch_width: Width in inches for PDF export
            pdf_inch_height: Height in inches for PDF export

        Returns:
            Dictionary with paths to exported files by format
        """
        path = Path(filename)
        if self.timestamp_files:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_filename = f"{path.stem}_{timestamp}{path.suffix}"
        else:
            final_filename = path.name

        output_path = self.output_dir / final_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        ext = output_path.suffix.lower()

        # Infer format from extension if not specified
        if formats is None:
            if ext == ".svg":
                formats = ["svg"]
            elif ext == ".pdf":
                formats = ["pdf"]
            elif ext == ".png":
                formats = ["png"]
            else:
                logger.warning(
                    f"Unsupported file extension '{ext}'. Use .svg, .png, or .pdf."
                )
                return {"success": False, "error": f"Unsupported extension: {ext}"}

        results = {}

        # Handle SVG export (native)
        if "svg" in formats:
            t0 = time.time()
            svg_path = output_path.with_suffix(".svg")
            self.scene.to_svg(filename=str(svg_path), frame_time=frame_time)
            elapsed = time.time() - t0

            logger.info(f'SVG exported to "{svg_path}"')
            logger.debug("Time taken for SVG export: {:.4f} seconds".format(elapsed))

            results["svg"] = str(svg_path)

        # Handle PNG/PDF exports (via converter)
        converter_formats = [fmt for fmt in formats if fmt != "svg"]
        if converter_formats:
            t0 = time.time()
            conv_results = self.converter.convert(
                self.scene,
                str(output_path),
                frame_time=frame_time,  # Pass time to converter
                formats=converter_formats,
                png_width_px=png_width_px,
                png_height_px=png_height_px,
                png_thumb_width_px=png_thumb_width_px,
                png_thumb_height_px=png_thumb_height_px,
                pdf_inch_width=pdf_inch_width,
                pdf_inch_height=pdf_inch_height,
            )
            elapsed = time.time() - t0
            logger.debug(
                f"Converter {self.converter.__class__.__name__} "
                f"for {converter_formats} took {elapsed:.4f}s"
            )
            if conv_results:
                results.update(conv_results)

        results["success"] = True
        return results

    def to_png(
        self,
        filename: str,
        frame_time: float = 0.0,
        width_px: Optional[int] = None,
        height_px: Optional[int] = None,
    ) -> str:
        """Export scene to PNG at specific time point.

        Convenience method for PNG-only export.
        """
        result = self.export(
            filename,
            frame_time=frame_time,
            formats=["png"],
            png_width_px=width_px,
            png_height_px=height_px,
        )
        logger.info(f"PNG exported to: \"{result.get('png')}\"")
        return result.get("png")

    def to_pdf(
        self,
        filename: str,
        frame_time: float = 0.0,
        pdf_inch_width: Optional[int] = None,
        pdf_inch_height: Optional[int] = None,
    ) -> str:
        """Export scene to PDF at specific time point.

        Convenience method for PDF-only export.
        """
        result = self.export(
            filename,
            frame_time=frame_time,
            formats=["pdf"],
            pdf_inch_width=pdf_inch_width,
            pdf_inch_height=pdf_inch_height,
        )
        logger.info(f"PDF exported to: \"{result.get('pdf')}\"")
        return result.get("pdf")

    # ========================================================================
    # ANIMATION EXPORTS
    # ========================================================================

    def to_frames(
        self,
        output_dir: str,
        filename_pattern: str = "frame_{:04d}",
        total_frames: int = 60,
        format: str = "svg",
        easing: Optional[Callable[[float], float]] = None,
        png_width_px: Optional[int] = None,
        png_height_px: Optional[int] = None,
        cleanup_intermediate: bool = True,
    ):
        """Export animation as frame sequence.

        Args:
            output_dir: Directory to save frames
            filename_pattern: Pattern for frame filenames (must include {:04d} or similar)
            total_frames: Number of frames to generate
            format: Format for frames ("svg", "png", or "pdf")
            easing: Optional easing function for animation
            png_width_px: Width for PNG frames
            png_height_px: Height for PNG frames
            cleanup_intermediate: If format is PNG, whether to delete SVG files

        Yields:
            Tuple of (frame_num, time) for progress tracking
        """
        frames_dir = Path(output_dir)
        frames_dir.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Generating {total_frames} frames in {format} format...")
        progress_step = max(1, total_frames // 10)

        # Track intermediate files for cleanup
        svg_files = []

        for frame_num in range(total_frames):
            if frame_num % progress_step == 0:
                progress = (frame_num / total_frames) * 100
                logger.info(f"Frame generation progress: {progress:.0f}%")

            # Calculate time
            t = frame_num / (total_frames - 1) if total_frames > 1 else 0.0
            if easing:
                t = easing(t)

            filename = filename_pattern.format(frame_num)

            if format == "svg":
                # Direct SVG export
                output_file = frames_dir / f"{filename}.svg"
                self.scene.to_svg(filename=str(output_file), frame_time=t, log=False)
            elif format == "png":
                # Export SVG first, then convert if cleanup is needed
                if cleanup_intermediate:
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
        if format == "png" and cleanup_intermediate and svg_files:
            logger.debug("Cleaning up intermediate SVG files...")
            for svg_file in svg_files:
                svg_file.unlink()

        logger.info(f"Frame generation complete: {total_frames} frames")

    def to_mp4(
        self,
        filename: str,
        total_frames: int = 60,
        framerate: int = 30,
        easing: Optional[Callable[[float], float]] = None,
        width_px: Optional[int] = None,
        height_px: Optional[int] = None,
        cleanup_intermediate_files: bool = True,
        codec: str = "libx264",
    ) -> str:
        """Export scene as video file.

        Args:
            filename: Output video filename (without extension)
            total_frames: Number of frames to generate
            framerate: Video framerate (fps)
            easing: Optional easing function
            png_width_px: Width for video frames
            png_height_px: Height for video frames
            cleanup_intermediate_files: Whether to delete frame images after encoding
            codec: Video codec (default: libx264 for MP4)

        Returns:
            Path to the exported video file
        """
        if not self._check_ffmpeg_available():
            logger.error("ffmpeg not available - cannot create video")
            raise RuntimeError("ffmpeg is required for video export")

        base_name = Path(filename).stem

        # Setup directories
        if self.timestamp_files:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_filename = f"{base_name}_{timestamp}"
        else:
            final_filename = base_name

        output_path = self.output_dir / f"{final_filename}.mp4"

        if cleanup_intermediate_files:
            temp_dir = (
                self.output_dir
                / f".temp_{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            frames_dir = temp_dir
        else:
            frames_dir = self.output_dir / f"{final_filename}_frames"

        frames_dir.mkdir(parents=True, exist_ok=True)

        # Generate PNG frames
        logger.info(f"Generating {total_frames} frames for video...")
        for frame_num, t in self.to_frames(
            output_dir=str(frames_dir),
            filename_pattern="frame_{:04d}",
            total_frames=total_frames,
            format="png",
            easing=easing,
            png_width_px=width_px,
            png_height_px=height_px,
            cleanup_intermediate=False,  # Keep frames for ffmpeg
        ):
            pass  # Progress is logged in to_frames

        # Create video with ffmpeg
        logger.debug("Encoding video with ffmpeg...")
        self._create_video_from_pngs(frames_dir, output_path, framerate, codec)

        # Cleanup
        if cleanup_intermediate_files:
            logger.debug("Cleaning up intermediate files...")
            shutil.rmtree(temp_dir)

        logger.info(f'Video exported to "{output_path}"')
        return str(output_path)

    def _create_video_from_pngs(
        self,
        png_dir: Path,
        output_path: Path,
        framerate: int,
        codec: str = "libx264",
    ) -> None:
        """Create video from PNG frames using ffmpeg"""
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
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.debug("Video encoding complete")
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg failed: {e.stderr}")
            raise
        except Exception as e:
            logger.error(f"Failed to create video: {e}")
            raise

    def _check_ffmpeg_available(self) -> bool:
        """Check if ffmpeg is available on the system"""
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
