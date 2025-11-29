# abstract base class for converting SVG to other formats
from __future__ import annotations


from abc import ABC, abstractmethod
from typing import Optional
from pathlib import Path

from vood.core.logger import get_logger

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vood.vscene.vscene import VScene

logger = get_logger()


class SVGConverter(ABC):
    """
    Abstract base class for converting SVG files to other formats like PNG and PDF.
    """

    def convert(
        self,
        scene: VScene,
        output_file: str,
        frame_time: Optional[float] = 0.0,
        formats: Optional[list[str]] = None,
        png_width_px: Optional[int] = None,
        png_height_px: Optional[int] = None,
        png_thumb_width_px: Optional[int] = None,
        png_thumb_height_px: Optional[int] = None,
        pdf_inch_width: Optional[float] = None,
        pdf_inch_height: Optional[float] = None,
    ) -> dict:
        if formats is None:
            if output_file.lower().endswith(".png"):
                formats = ["png"]
            elif output_file.lower().endswith(".pdf"):
                formats = ["pdf"]
            else:
                formats = ["png", "pdf"]

        output = {fmt: str(Path(output_file).with_suffix(f".{fmt}")) for fmt in formats}

        if "png_thumb" in formats:
            formats.remove("png_thumb")
            do_thumb = True
        else:
            do_thumb = False

        result = self._convert(
            scene,
            output,
            frame_time,
            formats,
            png_width_px=png_width_px,
            png_height_px=png_height_px,
            pdf_inch_width=pdf_inch_width,
            pdf_inch_height=pdf_inch_height,
        )

        if "png" in formats and do_thumb:

            try:
                from PIL import Image
            except ImportError:
                logger.warning("Pillow not installed. Skipping thumbnail generation. Install with: pip install Pillow")
            else:
                thumb_path = Path(result["png"]).with_suffix(".thumb.png")
                # create thumbnail for result['png']

                png_thumb_width_px, png_thumb_height_px = self._infer_dimensions(
                    scene, png_thumb_width_px, png_thumb_height_px
                )

                with Image.open(result["png"]) as img:
                    img.thumbnail((png_thumb_width_px, png_thumb_height_px))
                    img.save(thumb_path)

                    result["png_thumb"] = str(Path(output_file).with_suffix(".thumb.png"))

        return result

    def _convert(
        self,
        scene: VScene,
        output: dict,
        frame_time: Optional[float] = 0.0,
        formats: Optional[list] = ["png", "pdf"],
        png_width_px: Optional[int] = None,
        png_height_px: Optional[int] = None,
        pdf_inch_width: Optional[float] = None,
        pdf_inch_height: Optional[float] = None,
    ) -> dict:

        success = True

        ret = {}

        if "pdf" in formats:
            inch_width, inch_height = self._infer_dimensions(
                scene, pdf_inch_width, pdf_inch_height
            )
            _pdf = self._convert_to_pdf(
                scene,
                output["pdf"],
                frame_time=frame_time,
                inch_width=inch_width,
                inch_height=inch_height,
            )
            success = success and _pdf["success"]
            if _pdf["success"]:
                logger.debug(
                    f"PNG exported to {_pdf['output']} ({self.__class__.__name__})"
                )
                ret["pdf"] = _pdf["output"]

        if "png" in formats:

            width_px, height_px = self._infer_dimensions(
                scene, png_width_px, png_height_px
            )

            _png = self._convert_to_png(
                scene,
                output["png"],
                frame_time,
                width_px=width_px,
                height_px=height_px,
            )
            success = success and _png["success"]
            if _png["success"]:
                ret["png"] = _png["output"]
                logger.debug(
                    f"PNG exported to {_png['output']} ({self.__class__.__name__})"
                )

        if success:
            return {
                "success": True,
                "png": ret.get("png_output"),
                "pdf": ret.get("pdf_output"),
            }
        else:
            errors = ""
            if "_pdf" in locals() and _pdf is not None:
                if not _pdf.get("success", False):
                    errors += f"PDF Error: {_pdf.get('error', 'Unknown error')}\n"
            if "_png" in locals() and _png is not None:
                if not _png.get("success", False):
                    errors += f"PNG Error: {_png.get('error', 'Unknown error')}\n"
            logger.error(f"SVG export error {errors}")
            return {"success": False, "error": errors}

    @abstractmethod
    def _convert_to_png(
        self,
        scene: VScene,
        output_file: str,
        frame_time: Optional[float] = 0.0,
        width_px: Optional[int] = None,
        height_px: Optional[int] = None,
    ) -> dict:
        pass

    @abstractmethod
    def _convert_to_pdf(
        self,
        scene: VScene,
        output_file: str,
        frame_time: Optional[float] = 0.0,
        inch_width: Optional[int] = None,
        inch_height: Optional[int] = None,
    ) -> dict:
        pass

    def svg_html(self, svg_content):
        """
        Wrap SVG in HTML with optimized text rendering.
        """
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                * {{ 
                    margin: 0; 
                    padding: 0; 
                    box-sizing: border-box;
                    -webkit-font-smoothing: antialiased;
                    -moz-osx-font-smoothing: grayscale;
                }}
                html, body {{ 
                    width: 100%; 
                    height: 100%; 
                    overflow: hidden;
                }}
                body {{ 
                    margin: 0; 
                    padding: 0; 
                    background: white; 
                }}
                svg {{ 
                    display: block;
                    width: 100%;
                    height: 100%;
                    shape-rendering: crispEdges;
                    text-rendering: geometricPrecision;
                }}
            </style>
        </head>
        <body>
            {svg_content}
        </body>
        </html>
        """

    def _infer_dimensions(self, scene, width, height):
        """
        Infer missing width or height based on aspect ratio.
        """
        if width is None and height is None:
            return scene.width, scene.height
        elif width is not None and height is None:
            height = width * (scene.height / scene.width)
        elif height is not None and width is None:
            width = height * (scene.width / scene.height)
        return width, height

    def _get_write_scaled_svg_content(
        self,
        scene: VScene,
        frame_time: float,
        width: int,
        height: int,
        filename: Optional[str] = None,
        log: bool = True,
    ):
        """
        Generate scaled SVG content that fits within the target dimensions.

        Uses 'min' instead of 'max' to ensure content fits within bounds
        without overflow, maintaining aspect ratio.

        The scale factor is calculated as the minimum ratio needed to fit
        the scene within the target dimensions. This prevents content from
        being cut off or overflowing the viewport.
        """
        # Use MIN to fit content within bounds (not MAX which causes overflow)
        scale = min(
            width / scene.width,
            height / scene.height,
        )

        return scene.to_svg(
            render_scale=scale,
            frame_time=frame_time,
            width=width,
            height=height,
            filename=filename,
            log=log,
        )
