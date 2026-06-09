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

        self.setCentralWidget(label)

def main():
    app = QApplication(sys.argv)

    window = PDFEditWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
