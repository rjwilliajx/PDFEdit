from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)
from pathlib import Path
from debug_tools import debug_print
FONT_DIR = Path(__file__).resolve().parents[2] / "assets" / "fonts"


def show_add_signature_dialog(parent):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Add Signature")

    signature_input = QLineEdit()

    style_dropdown = QComboBox()
    style_dropdown.addItems([
            "Great Vibes",
            "Allura",
            "Dancing Script",
    ])

    signature_type_dropdown = QComboBox()
    signature_type_dropdown.addItems([
        "Conservative",
        "Typical",
        "Formal",
        "Showpiece",
    ])

    form_layout = QFormLayout()
    form_layout.addRow("Signature:", signature_input)
    form_layout.addRow("Style:", style_dropdown)
    form_layout.addRow("Signature Type:", signature_type_dropdown)

    add_button = QPushButton("Add Signature")
    add_button.clicked.connect(dialog.accept)

    layout = QVBoxLayout()
    layout.addLayout(form_layout)
    layout.addWidget(add_button)

    dialog.setLayout(layout)

    if dialog.exec():

        return (
        signature_input.text(),
        style_dropdown.currentText(),
        signature_type_dropdown.currentText(),
    )

    return None, None, None

def create_signature_content(parent):
    signature_text, style_name, signature_type = show_add_signature_dialog(parent)

    if not signature_text:
        return None

    font_map = {
        "Great Vibes": FONT_DIR / "GreatVibes-Regular.ttf",
        "Allura": FONT_DIR / "Allura-Regular.ttf",
        "Dancing Script": FONT_DIR / "DancingScript-Regular.ttf",
    }

    size_map = {
        "Conservative": 18,
        "Typical": 24,
        "Formal": 28,
        "Showpiece": 36,
    }

    debug_print(f"Using font: {font_map[style_name]}")
    debug_print(
        f"Signature type: {signature_type}, Size: {size_map[signature_type]}"
    )

    return {
        "type": "Signature",
        "text": signature_text,
        "fontfile": str(font_map[style_name]),
        "size": size_map[signature_type],
        "color": (0, 0, 0),
    }