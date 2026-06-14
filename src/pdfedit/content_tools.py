from PySide6.QtWidgets import QComboBox, QDialog, QFormLayout, QPushButton, QVBoxLayout

def show_add_content_menu(parent):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Add Content")

    content_type_dropdown = QComboBox()
    content_type_dropdown.addItems([
        "Text",
        "Date",
        "Signature",
        "Image",
        "QR Code",
    ])

    form_layout = QFormLayout()
    form_layout.addRow("Content Type:", content_type_dropdown)

    select_button = QPushButton("Select")
    select_button.clicked.connect(dialog.accept)

    layout = QVBoxLayout()
    layout.addLayout(form_layout)
    layout.addWidget(select_button)

    dialog.setLayout(layout)

    if dialog.exec():
        return content_type_dropdown.currentText()

    return None