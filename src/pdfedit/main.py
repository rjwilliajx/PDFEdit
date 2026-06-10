from asyncio import subprocess
import sys
from pathlib import Path
from tkinter import dialog

import fitz
from PySide6.QtGui import QPixmap, QImage, QPainter
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QScrollArea,
)
from numpy import matrix

class PDFEditWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.document = None
        
        self.current_page = 0
        self.zoom_level = 1.0

        self.setWindowTitle("PDFEdit")
        self.setMinimumSize(900, 700)

        self.label = QLabel(
             "PDFEdit\n\n"
             "Open a PDF using File → Open PDF.\n\n"
             "Use View to navigate pages, zoom, or close the PDF."

        )
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

    def previous_page(self):
        if self.document is None:
           return

        if self.current_page > 0:
           self.current_page -= 1
           self.render_page()

    def zoom_in(self):
        if self.document is None:
            return   
        
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

def main():
    app = QApplication(sys.argv)

    window = PDFEditWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
