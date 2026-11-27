

# * PDF file-management helper functions.

from pathlib import Path

import fitz

from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtGui import QPainter
import io

# * Open a PDF file and update the active window state.
# * Open a PDF file and update the active window state.
def open_pdf_file(window):
    file_path, _ = QFileDialog.getOpenFileName(
        window,
        "Open PDF",
        "",
        "PDF Files (*.pdf)"
    )

    if not file_path:
        return False

    window.document = fitz.open(file_path)
    window.label.setMargin(0)
    window.current_file_path = file_path
    window.current_page = 0
    window.has_unsaved_changes = False

    # * Clear temporary editing and placement state.
    window.selected_text_block = None
    window.selected_content = None
    window.selected_image_region = None
    window.movable_text_items.clear()
    window.selected_movable_text = None
    window.dragging_movable_text = False
    window.pending_content = None
    window.preview_content = None
    window.repeat_text_mode = False
    window.is_selecting_region = False

    window.render_page()

    return True


# * Save the active PDF to a new file path.
def save_pdf_as_file(window):
    if window.document is None:
        QMessageBox.information(
            window,
            "Save As",
            "Open a PDF before saving.",
        )
        return False

    default_path = ""

    if window.current_file_path:
        original = Path(window.current_file_path)
        default_path = str(
            original.with_name(f"{original.stem}_edited{original.suffix}")
        )

    file_path, _ = QFileDialog.getSaveFileName(
        window,
        "Save PDF As",
        default_path,
        "PDF Files (*.pdf)"
    )

    if not file_path:
        return False

    target_path = Path(file_path)

    if target_path.suffix.lower() != ".pdf":
        target_path = target_path.with_name(target_path.name + ".pdf")

    if window.current_file_path and target_path.resolve() == Path(window.current_file_path).resolve():
        QMessageBox.warning(
            window,
            "Choose a New File Name",
            "PDFEdit does not overwrite the original PDF. Please choose a different file name.",
        )
        return False

    try:
        # * Create an independent copy of the working PDF.
        pdf_bytes = window.document.tobytes(
            garbage=3,
            deflate=True,
            encryption=fitz.PDF_ENCRYPT_KEEP,
        )

        working_document = fitz.open(
            stream=io.BytesIO(pdf_bytes),
            filetype="pdf",
        )

        try:
            # * Commit movable text to its final position.
            for item in window.movable_text_items:
                page = working_document.load_page(item["page"])
                content = item["content"]

                page.insert_text(
                    (item["x"], item["y"]),
                    content["text"],
                    fontname=content["font"],
                    fontsize=content["size"],
                    color=content["color"],
                )

            working_document.save(
                str(target_path),
                garbage=3,
                deflate=True,
                encryption=fitz.PDF_ENCRYPT_KEEP,
            )

        finally:
            working_document.close()

    except Exception as error:
        QMessageBox.critical(
            window,
            "Save As Failed",
            f"PDFEdit could not save the PDF:\n\n{error}",
        )
        return False

    # * Load the saved PDF containing the committed text.
    saved_document = fitz.open(str(target_path))
    previous_document = window.document
    window.document = saved_document
    previous_document.close()

    # * Clear temporary editing and placement state.
    window.selected_text_block = None
    window.selected_content = None
    window.selected_image_region = None
    window.movable_text_items.clear()
    window.selected_movable_text = None
    window.dragging_movable_text = False
    window.pending_content = None
    window.preview_content = None
    window.repeat_text_mode = False
    window.is_selecting_region = False

    window.current_file_path = str(target_path)
    window.has_unsaved_changes = False
    window.render_page()

    return True


# * Print the currently rendered PDF page.
def print_pdf_file(window):
    if window.document is None:
        return False

    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    dialog = QPrintDialog(printer, window)

    if dialog.exec() != QPrintDialog.DialogCode.Accepted:
        return False

    painter = QPainter(printer)
    window.label.pixmap().render(painter)
    painter.end()

    return True


# * Close the active PDF and reset the display state.
def close_pdf_file(window):
    window.document = None
    window.current_page = 0
    window.current_file_path = None
    window.has_unsaved_changes = False
    window.selected_text_block = None
    window.selected_content = None
    window.selected_image_region = None
    window.movable_text_items.clear()
    window.selected_movable_text = None
    window.dragging_movable_text = False
    window.pending_content = None
    window.preview_content = None
    window.repeat_text_mode = False
    window.is_selecting_region = False
    window.label.clear()
    window.label.setMargin(30)
    window.label.setText("PDFEdit")
    window.page_status_label.setText("Page 0 of 0")

    return True


# * Reload the original PDF from disk.
# * Reload the active PDF from disk.
def reset_pdf_file(window):
    if window.current_file_path is None:
        return False

    window.document = fitz.open(window.current_file_path)
    window.current_page = 0
    window.has_unsaved_changes = False

    # * Clear temporary editing and placement state.
    window.selected_text_block = None
    window.selected_content = None
    window.selected_image_region = None
    window.movable_text_items.clear()
    window.selected_movable_text = None
    window.dragging_movable_text = False
    window.pending_content = None
    window.preview_content = None
    window.repeat_text_mode = False
    window.is_selecting_region = False

    window.render_page()

    return True