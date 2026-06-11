import sys

from PySide6.QtWidgets import QApplication

from window import PDFEditWindow

def main():

    app = QApplication(sys.argv)
    window = PDFEditWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
