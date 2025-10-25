from __future__ import annotations

from typing import Optional
from vood.converter.svg_converter import SVGConverter
from vood.utils.logger import get_logger
import time
import requests

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vood.vscene.vscene import VScene

logger = get_logger()


class PlaywrightHttpSvgConverter(SVGConverter):
    """
    SVGConverter implementation using an external HTTP Playwright render server.
    Connects to localhost:4000 by default.
    Supports PNG and PDF with correct width/height to maintain orientation.
    """

    def __init__(self, host: str = "localhost", port: int = 4000):
        super().__init__()
        self.host = host
        self.port = port
        self.base_url = f"http://{self.host}:{self.port}/render"

    def _convert(
        self,
        scene: VScene,
        outputs: dict,
        frame_time: Optional[float] = 0.0,
        formats: Optional[list] = ["png", "pdf"],
        png_width_px: Optional[int] = None,
        png_height_px: Optional[int] = None,
        pdf_inch_width: Optional[float] = None,
        pdf_inch_height: Optional[float] = None,
    ) -> dict:
        ret = {"success": False}

        try:
            t0_total = time.time()

            # --- PNG export ---
            if "png" in formats:
                width_px, height_px = self._infer_dimensions(
                    scene, png_width_px, png_height_px
                )
                svg_content = self._get_write_scaled_svg_content(
                    scene, frame_time, width_px, height_px
                )
                ok = self._render(
                    svg_content,
                    outputs["png"],
                    "png",
                    width=width_px,
                    height=height_px,
                )
                if ok:
                    ret["png"] = outputs["png"]

            # --- PDF export ---
            if "pdf" in formats and pdf_inch_width and pdf_inch_height:
                width_px = int(pdf_inch_width * 96)
                height_px = int(pdf_inch_height * 96)
                svg_content = self._get_write_scaled_svg_content(
                    scene, frame_time, width_px, height_px
                )
                ok = self._render(
                    svg_content,
                    outputs["pdf"],
                    frame_time,
                    "pdf",
                    width=width_px,
                    height=height_px,
                )
                if ok:
                    ret["pdf"] = outputs["pdf"]
            ret["success"] = True

            elapsed_total = time.time() - t0_total
            logger.debug(f"Total PlaywrightHttpSvgConverter time: {elapsed_total:.4f}s")
            return ret

        except Exception as e:
            logger.error(f"PlaywrightHttpSvgConverter error: {e}")
            return {"success": False, "error": str(e)}

    def _render(
        self,
        svg_content: str,
        output_path: str,
        type_: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ):
        """
        Send SVG to the HTTP render server and save the output.
        """
        t0 = time.time()
        try:
            payload = {"svg": svg_content, "type": type_}
            if width is not None and height is not None:
                payload.update({"width": width, "height": height})

            resp = requests.post(
                self.base_url,
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()

            with open(output_path, "wb") as f:
                f.write(resp.content)

            elapsed = time.time() - t0
            logger.debug(f"{type_.upper()} saved to {output_path} in {elapsed:.4f}s")
            return True

        except Exception as e:
            logger.error(f"Render failed for {type_}: {e}")
            return False

    def _convert_to_png(self, *args, **kwargs):
        pass

    def _convert_to_pdf(self, *args, **kwargs):
        pass
