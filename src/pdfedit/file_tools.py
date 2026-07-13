

# * PDF file-management helper functions.

from pathlib import Path

import fitz

from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtGui import QPainter


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
    window.selected_text_block = None
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
        window.document.save(
            str(target_path),
            garbage=3,
            deflate=True,
            encryption=fitz.PDF_ENCRYPT_KEEP,
        )

    except Exception as error:
        QMessageBox.critical(
            window,
            "Save As Failed",
            f"PDFEdit could not save the PDF:\n\n{error}",
        )
        return False

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
    window.label.clear()
    window.label.setMargin(30)
    window.label.setText("PDFEdit")
    window.page_status_label.setText("Page 0 of 0")

    return True


# * Reload the original PDF from disk.
def reset_pdf_file(window):
    if window.current_file_path is None:
        return False

    window.document = fitz.open(window.current_file_path)
    window.current_page = 0
    window.has_unsaved_changes = False
    window.selected_text_block = None
    window.render_page()

    return True