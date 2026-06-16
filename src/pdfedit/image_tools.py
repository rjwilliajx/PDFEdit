from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QPushButton,
    QVBoxLayout,
)


def create_image_content(parent):
    image_path, _ = QFileDialog.getOpenFileName(
        parent,
        "Select Image",
        "",
        "Images (*.png *.jpg *.jpeg *.bmp)"
    )

    if not image_path:
        return None

    dialog = QDialog(parent)
    dialog.setWindowTitle("Add Image")

    size_dropdown = QComboBox()
    size_dropdown.addItems([
        "Small",
        "Medium",
        "Large",
        "X-Large",
    ])

    form_layout = QFormLayout()
    form_layout.addRow("Image Size:", size_dropdown)

    add_button = QPushButton("Add Image")
    add_button.clicked.connect(dialog.accept)

    layout = QVBoxLayout()
    layout.addLayout(form_layout)
    layout.addWidget(add_button)

    dialog.setLayout(layout)

    if dialog.exec():
        return {
            "type": "Image",
            "image_path": image_path,
            "size": size_dropdown.currentText(),
        }

    return None