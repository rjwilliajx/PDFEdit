import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel

class PDFEditWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDFEdit")
        self.setMinimumSize(900, 700)

        label = QLabel("PDFEdit")
        label.setStyleSheet("font-size: 32px;")
        label.setMargin(30)

        self.setCentralWidget(label)

def main():
    app = QApplication(sys.argv)

    window = PDFEditWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
