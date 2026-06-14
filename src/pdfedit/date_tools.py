from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QPushButton,
    QVBoxLayout,
)

def show_add_date_dialog(parent):
    dialog = QDialog(parent)
    dialog.setWindowTitle("Add Date")

    date_picker = QDateEdit()
    date_picker.setCalendarPopup(True)
    date_picker.setDate(QDate.currentDate())

    format_dropdown = QComboBox()
    format_dropdown.addItems([
        "MM/DD/YYYY",
        "MM-DD-YYYY",
        "Month DD, YYYY",
        "YYYY-MM-DD",
    ])

    font_dropdown = QComboBox()
    font_dropdown.addItems(["Helvetica", "Times-Roman", "Courier"])

    size_dropdown = QComboBox()
    size_dropdown.addItems(["8", "10", "12", "14", "18", "24", "36"])

    color_dropdown = QComboBox()
    color_dropdown.addItems(["Black", "Red", "Blue"])

    form_layout = QFormLayout()
    form_layout.addRow("Date:", date_picker)
    form_layout.addRow("Format:", format_dropdown)
    form_layout.addRow("Font:", font_dropdown)
    form_layout.addRow("Size:", size_dropdown)
    form_layout.addRow("Color:", color_dropdown)

    add_button = QPushButton("Add Date")
    add_button.clicked.connect(dialog.accept)

    layout = QVBoxLayout()
    layout.addLayout(form_layout)
    layout.addWidget(add_button)

    dialog.setLayout(layout)

    if dialog.exec():
        return (
            date_picker.date(),
            format_dropdown.currentText(),
            font_dropdown.currentText(),
            int(size_dropdown.currentText()),
            color_dropdown.currentText(),
        )

    return None, None, None, None, None

def create_date_content(parent):
    selected_date, date_format, font_name, font_size, color_name = show_add_date_dialog(parent)

    if selected_date is None:
        return None

    if date_format == "MM/DD/YYYY":
        date_text = selected_date.toString("MM/dd/yyyy")
    elif date_format == "MM-DD-YYYY":
        date_text = selected_date.toString("MM-dd-yyyy")
    elif date_format == "Month DD, YYYY":
        date_text = selected_date.toString("MMMM d, yyyy")
    elif date_format == "YYYY-MM-DD":
        date_text = selected_date.toString("yyyy-MM-dd")
    else:
        date_text = selected_date.toString("MM/dd/yyyy")

    color_map = {
        "Black": (0, 0, 0),
        "Red": (1, 0, 0),
        "Blue": (0, 0, 1),
    }

    return {
        "type": "Date",
        "text": date_text,
        "font": font_name,
        "size": font_size,
        "color": color_map[color_name],
    }