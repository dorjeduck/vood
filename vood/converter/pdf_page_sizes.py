from enum import StrEnum


class PDFPageSizeInch(StrEnum):
    # page size in inches (calculated from 300 DPI)
    A0 = {"width": 33.11, "height": 46.81}
    A1 = {"width": 23.39, "height": 33.11}
    A2 = {"width": 16.54, "height": 23.39}
    A3 = {"width": 11.69, "height": 16.54}
    A4 = {"width": 8.27, "height": 11.69}
    A5 = {"width": 5.83, "height": 8.27}
    A6 = {"width": 4.13, "height": 5.83}

    LETTER = {"width": 8.50, "height": 11.00}
    LEGAL = {"width": 8.50, "height": 14.00}
    TABLOID = {"width": 11.00, "height": 17.00}

    LEDGER = {"width": 17.00, "height": 11.00}

    SQUARE_10 = {"width": 10.00, "height": 10.00}
    SQUARE_12 = {"width": 12.00, "height": 12.00}

    ART_PRINT_50x70 = {"width": 19.69, "height": 27.56}
    ART_PRINT_60x80 = {"width": 23.62, "height": 31.50}
    ART_PRINT_70x100 = {"width": 27.56, "height": 39.37}
