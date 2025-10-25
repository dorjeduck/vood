from __future__ import annotations

import tempfile
import subprocess

from vood.vscene.vscene import VScene
from vood.converter.svg_converter import SVGConverter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vood.vscene.vscene import VScene


class InkscapeSvgConverter(SVGConverter):
    """
    SVGConverter implementation using Inkscape CLI for conversions.
    """

    def _convert_to_pdf(
        self,
        scene: VScene,
        output_file: str,
        frame_time: float,
        inch_width: float,
        inch_height: float,
    ) -> dict:
        """Convert a VScene to PDF with page size in inches."""
        width_px = int(inch_width * 96)
        height_px = int(inch_height * 96)
        return self._convert_inkscape(
            scene, output_file, frame_time, width_px, height_px, mode="pdf"
        )

    def _convert_to_png(
        self,
        scene: VScene,
        output_file: str,
        frame_time: float,
        width_px: int,
        height_px: int,
    ) -> dict:
        """Convert a VScene to PNG with pixel dimensions."""
        return self._convert_inkscape(
            scene, output_file, frame_time, width_px, height_px, mode="png"
        )

    def _convert_inkscape(
        self,
        scene: VScene,
        output_file: str,
        frame_time: float,
        width: int,
        height: int,
        mode: str,
    ) -> dict:
        """Internal helper for Inkscape-based conversions."""
        try:
            with tempfile.NamedTemporaryFile(suffix=".svg", delete=True) as tmp:
                self._get_write_scaled_svg_content(
                    scene, frame_time, width, height, tmp.name, False
                )

                cmd = [
                    "inkscape",
                    tmp.name,
                    f"--export-type={mode}",
                    f"--export-width={int(width)}",
                    f"--export-height={int(height)}",
                    f"--export-filename={output_file}",
                ]

                subprocess.run(cmd, check=True)

            return {"success": True, "output": output_file}

        except Exception as e:
            return {"success": False, "error": str(e)}
