"""FastAPI-based rendering server using Playwright

Port of the Node.js render-server.js to Python with the same API contract.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from playwright.async_api import async_playwright

from vood.core.logger import get_logger

logger = get_logger()


class RenderRequest(BaseModel):
    """Request model for /render endpoint"""

    svg: str
    type: Literal["png", "pdf"]
    width: int
    height: int


app = FastAPI(
    title="Vood Playwright Render Server",
    description="HTTP server for rendering SVG to PNG/PDF using Playwright",
    version="1.0.0",
)


@app.post("/render")
async def render(request: RenderRequest) -> Response:
    """Render SVG to PNG or PDF

    Args:
        request: RenderRequest with svg content, type, width, height

    Returns:
        Binary PNG or PDF data

    Raises:
        HTTPException: If rendering fails or invalid type provided
    """
    if not request.svg or not request.type or not request.width or not request.height:
        raise HTTPException(
            status_code=400, detail="Missing svg, type, width, or height"
        )

    timestamp = datetime.now().isoformat()
    logger.info(f"[{timestamp}] Received render request for type: {request.type}")

    try:
        async with async_playwright() as p:
            # Launch Chromium with headless mode and no-sandbox for Docker/root compatibility
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = await browser.new_context()
            page = await context.new_page()

            # Set viewport and load SVG content
            await page.set_viewport_size({"width": request.width, "height": request.height})
            html_content = f'<html><body style="margin:0;padding:0;">{request.svg}</body></html>'
            await page.set_content(html_content)
            await page.wait_for_load_state("networkidle")

            # Render based on type
            if request.type == "png":
                buffer = await page.screenshot(full_page=True)
                content_type = "image/png"
            elif request.type == "pdf":
                buffer = await page.pdf(
                    width=f"{request.width}px",
                    height=f"{request.height}px",
                    print_background=True,
                    margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
                )
                content_type = "application/pdf"
            else:
                raise HTTPException(
                    status_code=400, detail=f"Unknown render type: {request.type}"
                )

            await browser.close()

        timestamp_done = datetime.now().isoformat()
        logger.info(f"[{timestamp_done}] Render done for type: {request.type}")

        return Response(content=buffer, media_type=content_type)

    except Exception as err:
        timestamp_error = datetime.now().isoformat()
        logger.error(f"[{timestamp_error}] Render error for type {request.type}: {err}")
        raise HTTPException(status_code=500, detail=str(err))


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring server status"""
    return {"status": "ok", "service": "playwright-render-server"}


def create_server(host: str = "localhost", port: int = 4000):
    """Create and configure the FastAPI server

    Args:
        host: Host to bind to (default: localhost)
        port: Port to listen on (default: 4000)

    Returns:
        Configured FastAPI app
    """
    return app


if __name__ == "__main__":
    import uvicorn

    # Run server directly for testing
    uvicorn.run(app, host="localhost", port=4000, log_level="info")
