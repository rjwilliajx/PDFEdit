from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


def show_add_signature_dialog(parent):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Add Signature")

    signature_input = QLineEdit()

    style_dropdown = QComboBox()
    style_dropdown.addItems([
        "Elegant Script",
        "Formal Script",
        "Handwritten",
        "Cursive",
        "Signature",
    ])

    form_layout = QFormLayout()
    form_layout.addRow("Signature:", signature_input)
    form_layout.addRow("Style:", style_dropdown)

    add_button = QPushButton("Add Signature")
    add_button.clicked.connect(dialog.accept)

    layout = QVBoxLayout()
    layout.addLayout(form_layout)
    layout.addWidget(add_button)

    dialog.setLayout(layout)

    if dialog.exec():
        return signature_input.text(), style_dropdown.currentText()

    return None, None

def create_signature_content(parent):
    signature_text, style_name = show_add_signature_dialog(parent)

    if not signature_text:
        return None

    font_map = {
        "Elegant Script": "Times-Roman",
        "Formal Script": "Helvetica",
        "Handwritten": "Courier",
        "Cursive": "Times-Roman",
        "Signature": "Helvetica",
    }

    return {

        "type": "Signature",
        "text": signature_text,
        "font": font_map[style_name],
        "size": 18,
        "color": (0, 0, 0),
    }