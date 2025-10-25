from enum import Enum


class ConverterType(Enum):
    PLAYWRIGHT_HTTP = "playwright_http"
    PLAYWRIGHT = "playwright"
    CAIROSVG = "cairosvg"
    INKSCAPE = "inkscape"
