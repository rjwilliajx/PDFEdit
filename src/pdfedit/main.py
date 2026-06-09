import sys
from pathlib import Path

import fitz
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
)

class PDFEditWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDFEdit")
        self.setMinimumSize(900, 700)

        self.label = QLabel("PDFEdit")
        self.label.setStyleSheet("font-size: 32px;")
        self.label.setMargin(30)

        self.setCentralWidget(self.label)
        file_menu = self.menuBar().addMenu("File")

        open_action = file_menu.addAction("Open PDF...")

        open_action.triggered.connect(self.open_pdf)

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
                    self,
                    "Open PDF",
                    "",
                    "PDF Files (*.pdf)"
     )
        if not file_path:
                return
                    
                print(file_path)
        document = fitz.open(file_path)

        self.label.setText(

            f"File: {Path(file_path).name}\n\nPages: {document.page_count}"

        )

def main():
    app = QApplication(sys.argv)

    window = PDFEditWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
