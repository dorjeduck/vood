from __future__ import annotations

from typing import Optional
from vood.converter.svg_converter import SVGConverter
from vood.core.logger import get_logger
from vood.config import get_config, ConfigKey
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

    Can optionally auto-start the server if not running (configurable via
    playwright_server.auto_start in config).
    """

    def __init__(self, host: str = "localhost", port: int = 4000, auto_start: Optional[bool] = None):
        super().__init__()
        config = get_config()
        self.host = host or config.get(ConfigKey.PLAYWRIGHT_SERVER_HOST, "localhost")
        self.port = port or config.get(ConfigKey.PLAYWRIGHT_SERVER_PORT, 4000)
        self.base_url = f"http://{self.host}:{self.port}/render"

        # Auto-start preference: explicit param > config > False (default)
        if auto_start is None:
            self.auto_start = config.get(ConfigKey.PLAYWRIGHT_SERVER_AUTO_START, False)
        else:
            self.auto_start = auto_start

        self._server_checked = False  # Track if we've checked/started server

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
                width_px, height_px = self._infer_dimensions(
                    scene, width_px, height_px
                )
                svg_content = self._get_write_scaled_svg_content(
                    scene, frame_time, width_px, height_px
                )
                ok = self._render(
                    svg_content,
                    outputs["pdf"],
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

    def _ensure_server_running(self):
        """Ensure the render server is running, auto-starting if configured

        Raises:
            RuntimeError: If server is not running and auto-start is disabled or fails
        """
        if self._server_checked:
            return  # Already checked/started this session

        # Check if server is responding
        try:
            health_url = f"http://{self.host}:{self.port}/health"
            resp = requests.get(health_url, timeout=2)
            if resp.status_code == 200:
                logger.debug("Playwright server is already running")
                self._server_checked = True
                return
        except requests.exceptions.RequestException:
            # Server not responding
            pass

        # Server not running - try auto-start if enabled
        if not self.auto_start:
            raise RuntimeError(
                f"Playwright render server is not running at {self.host}:{self.port}. "
                f"Start it with 'vood playwright-server start' or enable auto_start in config."
            )

        # Attempt auto-start
        logger.info("Auto-starting Playwright render server...")
        try:
            from vood.server.playwright.process_manager import ProcessManager

            manager = ProcessManager(host=self.host, port=self.port)
            if not manager.is_running():
                manager.start()
                # Wait a bit for server to be ready
                time.sleep(3)

                # Verify it's responding
                resp = requests.get(health_url, timeout=5)
                if resp.status_code != 200:
                    raise RuntimeError("Server started but not responding to health check")

                logger.info("Playwright server auto-started successfully")
                self._server_checked = True
            else:
                self._server_checked = True

        except Exception as e:
            raise RuntimeError(f"Failed to auto-start Playwright server: {e}")

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

        Automatically ensures server is running before attempting render.
        """
        # Ensure server is running (auto-start if configured)
        self._ensure_server_running()

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

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Cannot connect to Playwright server at {self.base_url}: {e}")
            logger.error("Ensure the server is running with 'vood playwright-server start'")
            return False
        except Exception as e:
            logger.error(f"Render failed for {type_}: {e}")
            return False

    def _convert_to_png(self, *args, **kwargs):
        pass

    def _convert_to_pdf(self, *args, **kwargs):
        pass