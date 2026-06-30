from pathlib import Path
import subprocess
import tempfile
import fitz
import time
from debug_tools import debug_print
from content_tools import show_add_content_menu
from text_tools import create_text_content
from date_tools import create_date_content
from signature_tools import create_signature_content
from image_tools import create_image_content
from qr_tools import generate_qr_code
from PIL import Image
from PySide6.QtGui import QFont, QImage, QImageReader, QPainter, QPixmap, QColor
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QLabel,
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
        
        
        file_menu = self.menuBar().addMenu("File")

        open_action = file_menu.addAction("Open PDF...")
        open_action.triggered.connect(self.open_pdf)

        save_action = file_menu.addAction("Save")
        save_action.setEnabled(False)

        save_as_action = file_menu.addAction("Save As...")
        save_as_action.triggered.connect(self.save_pdf_as)

        print_action = file_menu.addAction("Print PDF...")
        print_action.triggered.connect(self.print_pdf)

        edit_menu = self.menuBar().addMenu("Edit")

        add_content_action = edit_menu.addAction("Add Content")
        add_content_action.triggered.connect(self.add_content)

        edit_text_action = edit_menu.addAction("View/Edit Selected Text")
        edit_text_action.triggered.connect(self.view_edit_selected_text)

        view_menu = self.menuBar().addMenu("View")

        previous_action = view_menu.addAction("Previous Page")
        previous_action.triggered.connect(self.previous_page)

        next_action = view_menu.addAction("Next Page")
        next_action.triggered.connect(self.next_page)

        zoom_in_action = view_menu.addAction("Zoom In")
        zoom_in_action.triggered.connect(self.zoom_in)
        
        zoom_out_action = view_menu.addAction("Zoom Out")
        zoom_out_action.triggered.connect(self.zoom_out)

        close_action = view_menu.addAction("Close PDF")
        close_action.setShortcut("Esc")
        
        close_action.triggered.connect(self.close_pdf)

        reset_action = view_menu.addAction("Reset Document")
        reset_action.triggered.connect(self.reset_document)

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

    def handle_pdf_release(self, x, y):
        if self.document is None:
            return

        if self.preview_content is None:
            return

        print(f"Mouse released at X={x}, Y={y}")
        self.apply_preview_content()

    def handle_pdf_move(self, x, y):

        if self.preview_content is None:
            return

        self.preview_content["x"] = x
        self.preview_content["y"] = y
        self.render_page()

    def previous_page(self):
        if self.document is None:
           return

        if self.current_page > 0:
           self.current_page -= 1
           self.selected_text_block = None
           self.render_page()

    def zoom_in(self):
        self.zoom_level *= 1.25
        self.render_page()

    def zoom_out(self):
        if self.document is None:
            return
        
        self.zoom_level /= 1.25
        self.render_page()

    def next_page(self):
        if self.document is None:
            return

        if self.current_page < self.document.page_count - 1:
            self.current_page += 1
            self.selected_text_block = None
            self.render_page()

    def close_pdf(self):
        self.document = None
        self.current_page = 0
        self.current_file_path = None
        self.has_unsaved_changes = False
        self.selected_text_block = None
        self.label.clear()
        self.label.setMargin(30)
        self.label.setText("PDFEdit")

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF",
            "",
            "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        self.document = fitz.open(file_path)
        self.label.setMargin(0)
        self.current_file_path = file_path
        self.current_page = 0
        self.has_unsaved_changes = False
        self.selected_text_block = None
        self.render_page()

    def save_pdf_as(self):
        if self.document is None:
            QMessageBox.information(
                self,
                "Save As",
                "Open a PDF before saving.",
            )
            return

        default_path = ""

        if self.current_file_path:
            original = Path(self.current_file_path)
            default_path = str(
                original.with_name(f"{original.stem}_edited{original.suffix}")
            )

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF As",
            default_path,
            "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        target_path = Path(file_path)
        if target_path.suffix.lower() != ".pdf":
            target_path = target_path.with_name(target_path.name + ".pdf")

        if self.current_file_path and target_path.resolve() == Path(self.current_file_path).resolve():
            QMessageBox.warning(
                self,
                "Choose a New File Name",
                "PDFEdit does not overwrite the original PDF. Please choose a different file name.",
            )

            return

        try:
            self.document.save(
                str(target_path),
                garbage=3,
                deflate=True,
                encryption=fitz.PDF_ENCRYPT_KEEP,
            )
        except Exception as error:
            QMessageBox.critical(
                self,
                "Save As Failed",
                f"PDFEdit could not save the PDF:\n\n{error}",
            )
            return

        self.current_file_path = str(target_path)
        self.has_unsaved_changes = False
        self.render_page()

    def print_pdf(self):
        if self.document is None:
            return
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)

        if dialog.exec() != QPrintDialog.DialogCode.Accepted:
            return

        painter = QPainter(printer)
        self.label.pixmap().render(painter)
        painter.end()

    def reset_document(self):

            if self.current_file_path is None:
                return
            self.document = fitz.open(self.current_file_path)
            self.current_page = 0
            self.has_unsaved_changes = False
            self.render_page()

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

    def inspect_pdf_click(self, x, y):

        if self.document is None:
            self.selected_text_block = None
            print("No PDF is open.")
            return

        # load current page
        # convert click coordinates if needed
        # check text blocks/images
        # print what was clicked
        page = self.document.load_page(self.current_page)
        blocks = page.get_text("blocks")

        print(f"Found {len(blocks)} text blocks on page.")
        for block in blocks:
            x0, y0, x1, y1, text = block[:5]

            if x0 <= x <= x1 and y0 <= y <= y1:
                self.selected_text_block = {
                    "bounds": (x0, y0, x1, y1),
                    "text": text.strip(),
                    "font_name": None,
                    "font_size": None,
                    "color": None,
                }
                print("Clicked text block:")
                print(f"Bounds: X={x0:.2f} to {x1:.2f}, Y={y0:.2f} to {y1:.2f}")
                print(f"Text: {text.strip()}")
                self.render_page()
                return
        self.selected_text_block = None
        print("No editable text found at that location.")
        self.render_page()
        return

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
        x0, y0, x1, y1 = self.selected_text_block["bounds"]
        new_text = self.selected_text_block["text"]
        rect = fitz.Rect(x0, y0, x1, y1)

        chosen_font_size = None

        test_document = fitz.open("pdf", self.document.write())
        test_page = test_document.load_page(self.current_page)

        for font_size in range(10, 5, -1):
            test_result = test_page.insert_textbox(
                rect,
                new_text,
                fontsize=font_size,
                fontname="helv",
                color=(0, 0, 0),
            )

            if test_result >= 0:
                chosen_font_size = font_size

                break

        test_document.close()

        if chosen_font_size is None:
            print("Edited text is too large for the selected area.")

            return

        page = self.document.load_page(self.current_page)
        page.add_redact_annot(rect, fill=(1, 1, 1))
        page.apply_redactions()
        result = page.insert_textbox(
            rect,
            new_text,
            fontsize=chosen_font_size,
            fontname="helv",
            color=(0, 0, 0),
        )

        print(f"Text inserted at font size {chosen_font_size}.")
        print(f"Insert textbox result: {result}")

        self.has_unsaved_changes = True
        self.selected_text_block = None
        self.render_page()

    def apply_preview_content(self):
        if self.preview_content is None:
            return

        content = self.preview_content["content"]
        x = self.preview_content["x"]
        y = self.preview_content["y"]
        start_time = time.time()

        page = self.document.load_page(self.current_page)

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
                return

            original_width = image.width()
            original_height = image.height()

            if image_size == "Small":
                width = 75
            elif image_size == "Medium":
                width = 150
            elif image_size == "Large":
                width = 250
            elif image_size == "X-Large":
                width = 500
            else:
                width = 150

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

        self.preview_content = None
        self.has_unsaved_changes = True
        print(f"Before render: {time.time() - start_time:.2f}s")
        self.render_page()
        print(f"Total time: {time.time() - start_time:.2f}s")

    def render_page(self):
        if self.document is None:
            return

        page = self.document.load_page(self.current_page)
        
        matrix = fitz.Matrix(self.zoom_level, self.zoom_level)
        pix = page.get_pixmap(matrix=matrix)

        image = QImage(
            pix.samples,
            pix.width,
            pix.height,
            pix.stride,
            QImage.Format.Format_RGB888,
        )

        if self.selected_text_block is not None:
            x0, y0, x1, y1 = self.selected_text_block["bounds"]

            painter = QPainter(image)
            painter.setPen(QColor(0, 120, 215))
            painter.drawRect(
                int(x0 * self.zoom_level),
                int(y0 * self.zoom_level),
                int((x1 - x0) * self.zoom_level),
                int((y1 - y0) * self.zoom_level),
            )
            painter.end()

        if self.preview_content is not None:
            content = self.preview_content["content"]
            x = self.preview_content["x"]
            y = self.preview_content["y"]

            painter = QPainter(image)

            if content["type"] in ["Text", "Date"]:
                red, green, blue = content["color"]
                painter.setFont(QFont(content["font"], content["size"]))
                painter.setPen(QColor(
                    int(red * 255),
                    int(green * 255),
                    int(blue * 255),
                ))
                painter.drawText(x, y, content["text"])

            if content["type"] == "Signature":
                red, green, blue = content["color"]
                painter.setFont(QFont(content.get("font", "Zapfino"), content["size"]))
                painter.setPen(QColor(
                    int(red * 255),
                    int(green * 255),
                    int(blue * 255),
                ))
                painter.drawText(x, y, content["text"])

            if content["type"] == "Image":
                preview_image = QImage(content["image_path"])

                if not preview_image.isNull():
                    image_size = content["size"]

                    if image_size == "Small":
                        width = 75

                    elif image_size == "Medium":
                        width = 150

                    elif image_size == "Large":
                        width = 250

                    elif image_size == "X-Large":
                        width = 500

                    else:

                        width = 150

                    aspect_ratio = preview_image.height() / preview_image.width()
                    height = int(width * aspect_ratio)
                    painter.drawImage(
                        x,
                        y,
                        preview_image.scaled(width, height)
                    )

            painter.end()

        self.label.setPixmap(QPixmap.fromImage(image))
        self.label.adjustSize()
        self.setWindowTitle(

         f"PDFEdit - Page {self.current_page + 1} of {self.document.page_count}"

)