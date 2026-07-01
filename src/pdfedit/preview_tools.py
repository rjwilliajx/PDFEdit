

# * PDF preview and content-application helper functions.

import tempfile
import time

import fitz

from PySide6.QtGui import QFont, QImage, QImageReader, QPainter, QColor

from debug_tools import debug_print


# * Determine the display width for sized image content.
def get_image_width(image_size):
    if image_size == "Small":
        return 75

    if image_size == "Medium":
        return 150

    if image_size == "Large":
        return 250

    if image_size == "X-Large":
        return 500

    return 150


# * Apply pending preview content permanently to the active PDF page.
def apply_preview_content(window):
    if window.preview_content is None:
        return False

    content = window.preview_content["content"]
    x = window.preview_content["x"]
    y = window.preview_content["y"]
    start_time = time.time()

    page = window.document.load_page(window.current_page)

    if content["type"] in ["Text", "Date"]:
        page.insert_text(
            (x, y),
            content["text"],
            fontname=content["font"],
            fontsize=content["size"],
            color=content["color"],
        )

    elif content["type"] == "Signature":
        debug_print(
            f"Using signature fontfile: {content['fontfile']}"
        )

        page.insert_text(
            (x, y),
            content["text"],
            fontname="signaturefont",
            fontfile=content["fontfile"],
            fontsize=content["size"],
            color=content["color"],
        )

    elif content["type"] == "Image":
        image_path = content["image_path"]
        image_size = content["size"]

        reader = QImageReader(image_path)
        reader.setAutoTransform(True)
        image = reader.read()

        print(f"Image read: {time.time() - start_time:.2f}s")
        debug_print(f"Image loaded: isNull={image.isNull()}")

        if image.isNull():
            print("Image could not be loaded.")
            return False

        original_width = image.width()
        original_height = image.height()
        width = get_image_width(image_size)
        aspect_ratio = original_height / original_width
        height = int(width * aspect_ratio)

        image_rect = fitz.Rect(
            x,
            y,
            x + width,
            y + height,
        )

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            corrected_image_path = temp_file.name

        scaled_image = image.scaled(
            int(width),
            int(height),
        )

        scaled_image.save(corrected_image_path, "PNG")

        page.insert_image(
            image_rect,
            filename=corrected_image_path,
        )

        print(f"Image saved: {time.time() - start_time:.2f}s")

    window.preview_content = None
    window.has_unsaved_changes = True

    print(f"Before render: {time.time() - start_time:.2f}s")
    window.render_page()
    print(f"Total time: {time.time() - start_time:.2f}s")

    return True


# * Draw text-like preview content on the rendered page image.
def draw_text_preview(painter, content, x, y):
    red, green, blue = content["color"]
    painter.setFont(QFont(content["font"], content["size"]))
    painter.setPen(QColor(
        int(red * 255),
        int(green * 255),
        int(blue * 255),
    ))
    painter.drawText(x, y, content["text"])


# * Draw signature preview content on the rendered page image.
def draw_signature_preview(painter, content, x, y):
    red, green, blue = content["color"]
    painter.setFont(QFont(content.get("font", "Zapfino"), content["size"]))
    painter.setPen(QColor(
        int(red * 255),
        int(green * 255),
        int(blue * 255),
    ))
    painter.drawText(x, y, content["text"])


# * Draw image preview content on the rendered page image.
def draw_image_preview(painter, content, x, y):
    preview_image = QImage(content["image_path"])

    if preview_image.isNull():
        return

    width = get_image_width(content["size"])
    aspect_ratio = preview_image.height() / preview_image.width()
    height = int(width * aspect_ratio)

    painter.drawImage(
        x,
        y,
        preview_image.scaled(width, height)
    )


# * Draw any active preview content on the rendered page image.
def draw_preview_content(image, preview_content):
    if preview_content is None:
        return

    content = preview_content["content"]
    x = preview_content["x"]
    y = preview_content["y"]

    painter = QPainter(image)

    if content["type"] in ["Text", "Date"]:
        draw_text_preview(painter, content, x, y)

    elif content["type"] == "Signature":
        draw_signature_preview(painter, content, x, y)

    elif content["type"] == "Image":
        draw_image_preview(painter, content, x, y)

    painter.end()