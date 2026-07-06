import fitz

from debug_tools import debug_print
from content_tools import show_add_content_menu
from text_tools import create_text_content
from date_tools import create_date_content
from signature_tools import create_signature_content
from image_tools import create_image_content
from qr_tools import generate_qr_code

from menu_tools import setup_menus
from file_tools import (
    close_pdf_file,
    open_pdf_file,
    print_pdf_file,
    reset_pdf_file,
    save_pdf_as_file,
)
from preview_tools import apply_preview_content as apply_preview
from selection_tools import build_selected_text_block
from text_edit_tools import delete_content_block
from text_edit_tools import replace_selected_text as replace_text_block
from viewer_tools import (
    go_to_next_page,
    go_to_previous_page,
    render_pdf_page,
    zoom_page_in,
    zoom_page_out,
)

from PySide6.QtWidgets import (
    QLabel,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QScrollArea,
)


class ClickableLabel(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.press_handler = None
        self.move_handler = None
        self.release_handler = None

    def mousePressEvent(self, event):
        x = int(event.position().x())
        y = int(event.position().y())

        if self.press_handler:
            self.press_handler(x, y)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        x = int(event.position().x())
        y = int(event.position().y())

        if self.move_handler:
            self.move_handler(x, y)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        x = int(event.position().x())
        y = int(event.position().y())

        if self.release_handler:
            self.release_handler(x, y)

        super().mouseReleaseEvent(event)


class PDFEditWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.document = None
        self.pending_text = None
        self.pending_font = None
        self.pending_size = None
        self.pending_color = None
        self.pending_content = None
        self.preview_content = None
        self.selected_text_block = None
        self.is_dragging_preview = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        self.current_page = 0
        self.zoom_level = 1.0
        self.current_file_path = None
        self.has_unsaved_changes = False

        self.setWindowTitle("PDFEdit")
        self.setMinimumSize(900, 700)

        self.last_click_x = 72
        self.last_click_y = 72

        self.label = ClickableLabel()
        self.label.setText(
            "PDFEdit\n\n"
            "Open a PDF using File → Open PDF.\n\n"
            "Use View to navigate pages, zoom, or close the PDF."
        )

        self.label.press_handler = self.handle_pdf_click
        self.label.move_handler = self.handle_pdf_move
        self.label.release_handler = self.handle_pdf_release
        self.label.setStyleSheet("font-size: 16px;")
        self.label.setMargin(30)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.label)
        self.scroll_area.setWidgetResizable(True)

        self.setCentralWidget(self.scroll_area)

        setup_menus(self)

    def add_content(self):
        content_type = show_add_content_menu(self)

        if content_type is None:
            return

        print(f"Selected Content Type: {content_type}")

        if content_type == "Text":
            self.add_text()

        elif content_type == "Date":
            self.add_date()

        elif content_type == "Signature":
            self.add_signature()

        elif content_type == "Image":
            self.add_image()

        elif content_type == "QR Code":
            self.add_qr_code()

        else:
            print(f"{content_type} selected")

    def add_text(self):
        if self.document is None:
            return

        content = create_text_content(self)

        if content is None:
            return

        self.pending_content = content
        print("Click on the PDF to place the content.")

    def add_date(self):
        if self.document is None:
            return

        content = create_date_content(self)

        if content is None:
            return

        self.pending_content = content
        print("Click on the PDF to place the content.")

    def add_signature(self):
        if self.document is None:
            return

        content = create_signature_content(self)

        if content is None:
            return

        self.pending_content = content
        print("Click on the PDF to place the content.")

    def add_image(self):
        if self.document is None:
            return

        content = create_image_content(self)

        if content is None:
            return

        self.pending_content = content
        print("Click on the PDF to place the content.")

    def add_qr_code(self):
        if self.document is None:
            return

        qr_text, ok = QInputDialog.getText(
            self,
            "Add QR Code",
            "Enter URL or text:"
        )

        if not ok or not qr_text.strip():
            return

        qr_path = generate_qr_code(qr_text.strip())

        self.pending_content = {
            "type": "Image",
            "image_path": qr_path,
            "size": "Small",
        }

        print("Click on the PDF to place the QR code.")

    def open_pdf(self):
        open_pdf_file(self)

    def save_pdf_as(self):
        save_pdf_as_file(self)

    def print_pdf(self):
        print_pdf_file(self)

    def close_pdf(self):
        close_pdf_file(self)

    def reset_document(self):
        reset_pdf_file(self)

    def previous_page(self):
        go_to_previous_page(self)

    def next_page(self):
        go_to_next_page(self)

    def zoom_in(self):
        zoom_page_in(self)

    def zoom_out(self):
        zoom_page_out(self)

    def render_page(self):
        render_pdf_page(self)

    def handle_pdf_click(self, x, y):
        self.last_click_x = x
        self.last_click_y = y

        debug_print(f"Stored X={self.last_click_x}, Stored Y={self.last_click_y}")
        debug_print(f"Pending content at click: {self.pending_content}")

        if self.pending_content is None:
            self.inspect_pdf_click(x, y)
            return

        self.preview_content = {
            "content": self.pending_content,
            "x": x,
            "y": y,
        }

        self.pending_content = None

        print(f"Preview content placed at X={x}, Y={y}")
        self.render_page()

    def handle_pdf_move(self, x, y):
        if self.preview_content is None:
            return

        self.preview_content["x"] = x
        self.preview_content["y"] = y
        self.render_page()

    def handle_pdf_release(self, x, y):
        if self.document is None:
            return

        if self.preview_content is None:
            return

        print(f"Mouse released at X={x}, Y={y}")
        self.apply_preview_content()

    def apply_preview_content(self):
        apply_preview(self)

    def inspect_pdf_click(self, x, y):
        if self.document is None:
            self.selected_text_block = None
            print("No PDF is open.")
            return

        page = self.document.load_page(self.current_page)
        blocks = page.get_text("blocks")
        self.selected_text_block = build_selected_text_block(page, x, y)

        print(f"Found {len(blocks)} text blocks on page.")

        if self.selected_text_block is None:
            print("No editable text found at that location.")
            self.render_page()
            return

        x0, y0, x1, y1 = self.selected_text_block["bounds"]

        print("Clicked text block:")
        print(f"Bounds: X={x0:.2f} to {x1:.2f}, Y={y0:.2f} to {y1:.2f}")
        print(f"Text: {self.selected_text_block['text']}")
        print(
            f"Font: {self.selected_text_block['font_name']}, "
            f"Size: {self.selected_text_block['font_size']}, "
            f"Color: {self.selected_text_block['color']}"
        )
        print(f"Line height: {self.selected_text_block['line_height']}")

        self.render_page()

    def view_edit_selected_text(self):
        if self.selected_text_block is None:
            QMessageBox.information(
                self,
                "No Text Selected",
                "Please select a text block first."
            )
            return

        selected_block = self.selected_text_block

        edited_text, ok = QInputDialog.getMultiLineText(
            self,
            "View/Edit Selected Text",
            "Selected Text:",
            selected_block["text"],
        )

        if not ok:
            return

        selected_block["text"] = edited_text
        self.selected_text_block = selected_block

        print("Updated selected text:")
        print(self.selected_text_block["text"])

        self.replace_selected_text()

    def replace_selected_text(self):
        if self.selected_text_block is None:
            return

        replaced = replace_text_block(
            self.document,
            self.current_page,
            self.selected_text_block,
        )

        if not replaced:
            return

        self.has_unsaved_changes = True
        self.selected_text_block = None
        self.render_page()

    def delete_content_block(self):
        if self.selected_text_block is None:
            QMessageBox.information(
                self,
                "No Text Selected",
                "Please select a text block first."
            )
            return

        confirmation_box = QMessageBox(self)
        confirmation_box.setWindowTitle("Delete Content Block")
        confirmation_box.setIcon(QMessageBox.Icon.Warning)
        confirmation_box.setText("Delete Content Block")
        confirmation_box.setInformativeText(
            "This will permanently delete the selected content block from the PDF.\n\n"
            "This action cannot be undone.\n\n"
            "Do you want to continue?"
        )
        confirmation_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        confirmation_box.setDefaultButton(QMessageBox.StandardButton.No)
        confirmation = confirmation_box.exec()
        
        if confirmation != QMessageBox.StandardButton.Yes:
            return

        deleted = delete_content_block(
            self.document,
            self.current_page,
            self.selected_text_block,
        )

        if not deleted:
            return

        self.has_unsaved_changes = True
        self.selected_text_block = None
        self.render_page()