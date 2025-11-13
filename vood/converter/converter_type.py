from enum import StrEnum


class ConverterType(StrEnum):
    PLAYWRIGHT_HTTP = "playwright_http"
    PLAYWRIGHT = "playwright"
    CAIROSVG = "cairosvg"
    INKSCAPE = "inkscape"
    IMAGEMAGICK = "imagemagick"
