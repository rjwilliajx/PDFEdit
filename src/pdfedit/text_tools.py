from PySide6.QtWidgets import QComboBox, QDialog, QFormLayout, QLineEdit, QPushButton, QVBoxLayout
from PySide6.QtGui import QFontDatabase

def show_add_text_dialog(parent):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Add Text")

    text_input = QLineEdit()
    font_dropdown = QComboBox()
    font_dropdown.addItems(["Helvetica", "Times-Roman", "Courier"])
    size_dropdown = QComboBox()
    size_dropdown.addItems(["8", "10", "12", "14", "18", "24", "36"])
    color_dropdown = QComboBox()

    color_dropdown.addItems(["Black", "Red", "Blue"])

    form_layout = QFormLayout()
    form_layout.addRow("Text:", text_input)
    form_layout.addRow("Font:", font_dropdown)
    form_layout.addRow("Size:", size_dropdown)
    form_layout.addRow("Color:", color_dropdown)

    add_button = QPushButton("Add Text")
    add_button.clicked.connect(dialog.accept)

    layout = QVBoxLayout()
    layout.addLayout(form_layout)
    layout.addWidget(add_button)

    dialog.setLayout(layout)

    if dialog.exec():
        return text_input.text(), font_dropdown.currentText(), int(size_dropdown.currentText()), color_dropdown.currentText()
    return None, None, None, None