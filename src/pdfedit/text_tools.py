from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QTextEdit,
    QDoubleSpinBox,
    QColorDialog,
    QDialogButtonBox,
)

from font_tools import resolve_insert_font


def show_add_text_dialog(
    parent,
    default_font="Helvetica",
    default_size=8,
    default_color="Black",
):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Add Text")

    text_input = QLineEdit()
    font_dropdown = QComboBox()
    font_dropdown.addItems(["Helvetica", "Times-Roman", "Courier"])
    size_dropdown = QComboBox()
    size_dropdown.addItems(["8", "10", "12", "14", "18", "24", "36"])
    color_dropdown = QComboBox()

    color_dropdown.addItems(["Black", "Red", "Blue"])
    font_dropdown.setCurrentText(default_font)
    size_dropdown.setCurrentText(str(default_size))
    color_dropdown.setCurrentText(default_color)

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

def create_text_content(

    parent,
    default_font="Helvetica",
    default_size=8,
    default_color="Black",
):
    text, font_name, font_size, color_name = show_add_text_dialog(
        parent,
        default_font=default_font,
        default_size=default_size,
        default_color=default_color,
    )

    if not text:
        return None

    color_map = {
        "Black": (0, 0, 0),
        "Red": (1, 0, 0),
        "Blue": (0, 0, 1),
    }

    return {
        "type": "Text",
        "text": text,
        "font": font_name,
        "size": font_size,
        "color": color_map[color_name],
    }

# * Edit existing PDF text and its formatting.
def show_edit_text_dialog(parent, selected_block):

    dialog = QDialog(parent)
    dialog.setWindowTitle("Edit Selected Text")
    dialog.setMinimumWidth(450)

    # * Populate the existing text.
    text_input = QTextEdit()
    text_input.setPlainText(selected_block["text"])

    # * Provide supported PDF fonts.
    font_options = {
        "Helvetica": "helv",
        "Helvetica-Bold": "hebo",
        "Helvetica-Oblique": "heit",
        "Helvetica-BoldOblique": "hebi",
        "Times-Roman": "tiro",
        "Times-Bold": "tibo",
        "Times-Italic": "tiit",
        "Times-BoldItalic": "tibi",
        "Courier": "cour",
        "Courier-Bold": "cobo",
        "Courier-Oblique": "coit",
        "Courier-BoldOblique": "cobi",
    }

    font_dropdown = QComboBox()
    font_dropdown.addItems(list(font_options.keys()))

    existing_font = resolve_insert_font(
        selected_block.get("font_name")
    )

    for font_name, font_code in font_options.items():
        if font_code == existing_font:
            font_dropdown.setCurrentText(font_name)
            break

    # * Support custom and fractional font sizes.
    size_input = QDoubleSpinBox()
    size_input.setRange(1, 144)
    size_input.setDecimals(2)
    size_input.setSingleStep(1)
    size_input.setValue(
        selected_block.get("font_size") or 10
    )

    # * Initialize the existing text color.
    existing_color = selected_block.get("color") or 0

    selected_color = QColor(
        (existing_color >> 16) & 255,
        (existing_color >> 8) & 255,
        existing_color & 255,
    )

    color_button = QPushButton()

    def update_color_button():
        color_button.setText(
            selected_color.name().upper()
        )

        color_button.setStyleSheet(
            f"border: 2px solid {selected_color.name()};"
            "padding: 6px;"
        )

    def choose_color():
        nonlocal selected_color

        new_color = QColorDialog.getColor(
            selected_color,
            dialog,
            "Select Text Color",
        )

        if new_color.isValid():
            selected_color = new_color
            update_color_button()

    color_button.clicked.connect(choose_color)
    update_color_button()

    # * Build the formatting form.
    form_layout = QFormLayout()
    form_layout.addRow("Text:", text_input)
    form_layout.addRow("Font:", font_dropdown)
    form_layout.addRow("Size:", size_input)
    form_layout.addRow("Color:", color_button)

    buttons = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok
        | QDialogButtonBox.StandardButton.Cancel
    )

    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)

    layout = QVBoxLayout()
    layout.addLayout(form_layout)
    layout.addWidget(buttons)

    dialog.setLayout(layout)

    if not dialog.exec():
        return None

    edited_text = text_input.toPlainText()

    if not edited_text.strip():
        return None

    # * Return updated formatting without modifying the original selection.
    updated_block = selected_block.copy()

    updated_block["text"] = edited_text
    updated_block["font_name"] = font_dropdown.currentText()
    updated_block["font_size"] = size_input.value()

    updated_block["color"] = (
        (selected_color.red() << 16)
        | (selected_color.green() << 8)
        | selected_color.blue()
    )

    return updated_block