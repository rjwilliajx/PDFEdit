# * PDF viewer and page-rendering helper functions.

import fitz

from PySide6.QtGui import QImage, QPainter, QPixmap, QColor

from preview_tools import draw_preview_content


# * Move to the previous PDF page when available.
def go_to_previous_page(window):

    if window.document is None:
        return False

    if window.current_page > 0:
        window.current_page -= 1
        window.selected_content = None
        window.selected_text_block = None
        window.render_page()
        return True

    return False


# * Move to the next PDF page when available.
def go_to_next_page(window):

    if window.document is None:
        return False

    if window.current_page < window.document.page_count - 1:
        window.current_page += 1
        window.selected_content = None
        window.selected_text_block = None
        window.render_page()
        return True

    return False


# * Increase the current PDF zoom level.
def zoom_page_in(window):

    if window.document is None:
        return False

    window.zoom_level *= 1.25
    window.render_page()

    return True


# * Decrease the current PDF zoom level.
def zoom_page_out(window):

    if window.document is None:
        return False

    window.zoom_level /= 1.25
    window.render_page()

    return True


# * Draw the selected text-block outline on the rendered page image.
def draw_selected_content(image, selected_content, zoom_level):
    if selected_content is None:
        return

    x0, y0, x1, y1 = selected_content["bounds"]

    painter = QPainter(image)
    painter.setPen(QColor(0, 120, 215))
    painter.drawRect(
        int(x0 * zoom_level),
        int(y0 * zoom_level),
        int((x1 - x0) * zoom_level),
        int((y1 - y0) * zoom_level),
    )
    painter.end()


# * Render the active PDF page into the main display label.
def render_pdf_page(window):

    if window.document is None:
        return False

    page = window.document.load_page(window.current_page)

    matrix = fitz.Matrix(
        window.zoom_level,
        window.zoom_level,
    )

    pix = page.get_pixmap(matrix=matrix)

    image = QImage(
        pix.samples,
        pix.width,
        pix.height,
        pix.stride,
        QImage.Format.Format_RGB888,
    )

    draw_selected_content(
        image,
        window.selected_content,
        window.zoom_level,
    )

    draw_preview_content(
        image,
        window.preview_content,
    )

    window.label.setPixmap(QPixmap.fromImage(image))
    window.label.adjustSize()

    window.page_status_label.setText(
        f"Page {window.current_page + 1} of {window.document.page_count}"
    )

    return True