from __future__ import annotations
import time
from typing import Optional
from vood.converter.svg_converter import SVGConverter
from playwright.sync_api import sync_playwright

from vood.utils.logger import get_logger

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vood.vscene.vscene import VScene

logger = get_logger()


class PlaywrightSvgConverter(SVGConverter):
    """
    SVGConverter implementation using Playwright for conversions.
    """

    def _convert(
        self,
        scene: VScene,
        outputs: dict,
        frame_time: Optional[float] = 0.0,
        formats: Optional[list] = ["png", "pdf"],
        png_width_px: Optional[int] = None,
        png_height_px: Optional[int] = None,
        pdf_inch_width: Optional[int] = None,
        pdf_inch_height: Optional[int] = None,
    ) -> dict:
        """
        Export both PNG and PDF in a single Chromium session.
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
                context = browser.new_context()
                ret = {}

                def render_page(width: int, height: int, content: str):
                    page = context.new_page()
                    page.set_viewport_size({"width": width, "height": height})
                    page.set_content(self.svg_html(content))
                    page.wait_for_load_state("networkidle")
                    return page

                # PNG

                if "png" in formats:
                    t0 = time.time()
                    width_px, height_px = self._infer_dimensions(
                        scene, png_width_px, png_height_px
                    )
                    logger.debug(f"Rendering PNG with size {width_px}x{height_px}")

                    svg_content = self._get_write_scaled_svg_content(
                        scene, frame_time, width_px, height_px
                    )
                    page = render_page(width_px, height_px, svg_content)
                    page.screenshot(path=outputs["png"], full_page=True)
                    page.close()
                    elapsed = time.time() - t0
                    ret["png"] = outputs["png"]
                    logger.debug(
                        f"PNG exported to {outputs['png']} (PlaywrightSvgConverter) in {elapsed:.4f} seconds"
                    )

                # PDF
                if "pdf" in formats and pdf_inch_width and pdf_inch_height:
                    t0 = time.time()
                    # Viewport for rendering in pixels
                    width_px = int(pdf_inch_width * 96)
                    height_px = int(pdf_inch_height * 96)
                    width_px, height_px = self._infer_dimensions(
                        scene, width_px, height_px
                    )
                    svg_content = self._get_write_scaled_svg_content(
                        scene, frame_time, width_px, height_px
                    )
                    page = render_page(width_px, height_px, svg_content)
                    page.pdf(
                        path=outputs["pdf"],
                        width=f"{pdf_inch_width}in",
                        height=f"{pdf_inch_height}in",
                        margin={
                            "top": "0px",
                            "bottom": "0px",
                            "left": "0px",
                            "right": "0px",
                        },
                        print_background=True,
                    )
                    page.close()
                    elapsed = time.time() - t0
                    ret["pdf"] = outputs["pdf"]
                    logger.debug(
                        f"PNG exported to {outputs['pdf']} (PlaywrightSvgConverter) in {elapsed:.4f} seconds"
                    )

                browser.close()
                ret["success"] = True
                return ret

        except Exception as e:
            logger.error(f"PlaywrightSvgConverter error: {e}")
            return {"success": False, "error": str(e)}

    def _convert_to_png(self, *args, **kwargs):
        # not called, handled by _convert
        pass

    def _convert_to_pdf(self, *args, **kwargs):
        # not called, handled by _convert
        pass
