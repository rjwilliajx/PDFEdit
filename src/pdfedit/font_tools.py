# * Font and text-formatting helper functions.


# * Resolve the best available font for text insertion.
def resolve_insert_font(detected_font):

    if detected_font is None:
        return "helv"

    font_name = str(detected_font).lower()

    supported_fonts = {
        "courier": "cour",
        "courier-bold": "cobo",
        "courier-oblique": "coit",
        "courier-boldoblique": "cobi",
        "helvetica": "helv",
        "helvetica-bold": "hebo",
        "helvetica-oblique": "heit",
        "helvetica-boldoblique": "hebi",
        "times-roman": "tiro",
        "times-bold": "tibo",
        "times-italic": "tiit",
        "times-bolditalic": "tibi",
    }

    if font_name in supported_fonts:
        return supported_fonts[font_name]

    monospace_keywords = [
        "courier",
        "consolas",
        "mono",
        "ocr",
    ]

    serif_keywords = [
        "times",
        "georgia",
        "garamond",
        "cambria",
        "baskerville",
        "serif",
    ]

    sans_keywords = [
        "arial",
        "helvetica",
        "calibri",
        "verdana",
        "tahoma",
        "segoe",
        "sans",
    ]

    if any(keyword in font_name for keyword in monospace_keywords):
        print(f"Detected font '{detected_font}' is unavailable. Using Courier fallback.")
        return "cour"

    if any(keyword in font_name for keyword in serif_keywords):
        print(f"Detected font '{detected_font}' is unavailable. Using Times fallback.")
        return "tiro"

    if any(keyword in font_name for keyword in sans_keywords):
        print(f"Detected font '{detected_font}' is unavailable. Using Helvetica fallback.")
        return "helv"

    print(f"Detected font '{detected_font}' is unavailable. Using Helvetica fallback.")
    return "helv"


# * Convert a PDF integer color value to an RGB tuple.
def pdf_color_to_rgb(color):

    if color is None:
        return (0, 0, 0)

    return (
        ((color >> 16) & 255) / 255,
        ((color >> 8) & 255) / 255,
        (color & 255) / 255,
    )


# * Convert line height to a PyMuPDF line-height factor.
def line_height_to_factor(line_height, font_size):

    if font_size is None:
        font_size = 10

    if line_height is None:
        return 1.2

    return line_height / font_size