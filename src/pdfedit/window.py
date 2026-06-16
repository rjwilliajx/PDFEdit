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
from PIL import Image
from PySide6.QtGui import QImage, QImageReader, QPainter, QPixmap
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QScrollArea,
)



class ClickableLabel(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.click_handler = None

    def mousePressEvent(self, event):
        x = int(event.position().x())
        y = int(event.position().y())
        if self.click_handler:
            self.click_handler(x, y)

        super().mousePressEvent(event)

class PDFEditWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.document = None
        self.pending_text = None
        self.pending_font = None
        self.pending_size = None
        self.pending_color = None
        self.pending_content = None

        self.current_page = 0
        self.zoom_level = 1.0
        self.current_file_path = None

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

        self.label.click_handler = self.handle_pdf_click
        self.label.setStyleSheet("font-size: 16px;")
        self.label.setMargin(30)

        self.scroll_area = QScrollArea()

        self.scroll_area.setWidget(self.label)
        self.scroll_area.setWidgetResizable(True)

        self.setCentralWidget(self.scroll_area)
        
        
        file_menu = self.menuBar().addMenu("File")

        open_action = file_menu.addAction("Open PDF...")
        open_action.triggered.connect(self.open_pdf)

        print_action = file_menu.addAction("Print PDF...")
        print_action.triggered.connect(self.print_pdf)

        edit_menu = self.menuBar().addMenu("Edit")

        add_content_action = edit_menu.addAction("Add Content")
        add_content_action.triggered.connect(self.add_content)

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

    def previous_page(self):
        if self.document is None:
           return

        if self.current_page > 0:
           self.current_page -= 1
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
            self.render_page()

    def close_pdf(self):
        self.document = None
        self.current_page = 0
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
            self.render_page()
    
    def handle_pdf_click(self, x, y):
        self.last_click_x = x
        self.last_click_y = y

        debug_print(f"Stored X={self.last_click_x}, Stored Y={self.last_click_y}")
        debug_print(f"Pending content at click: {self.pending_content}")

        if self.pending_content is None:
            return

        page = self.document.load_page(self.current_page)

        if self.pending_content["type"] in ["Text", "Date"]:
            page.insert_text(
                (x, y),
                self.pending_content["text"],
                fontname=self.pending_content["font"],
                fontsize=self.pending_content["size"],
                color=self.pending_content["color"],
            )

        elif self.pending_content["type"] == "Signature":

            debug_print(
                f"Using signature fontfile: {self.pending_content['fontfile']}"
            )

            page.insert_text(
                (x, y),
                self.pending_content["text"],
                fontname="signaturefont",
                fontfile=self.pending_content["fontfile"],
                fontsize=self.pending_content["size"],
                color=self.pending_content["color"],
            )
        
        elif self.pending_content["type"] == "Image":
            start_time = time.time()
            
            image_path = self.pending_content["image_path"]
            image_size = self.pending_content["size"]

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

        

        self.pending_content = None
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



        self.label.setPixmap(QPixmap.fromImage(image))
        self.label.adjustSize()
        self.setWindowTitle(

         f"PDFEdit - Page {self.current_page + 1} of {self.document.page_count}"

)