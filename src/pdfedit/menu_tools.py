# * PDF application menu helper functions.

def setup_menus(window):
    # * Create all application menus.

    setup_file_menu(window)
    setup_edit_menu(window)
    setup_view_menu(window)


def setup_file_menu(window):
    # * Create the File menu.

    file_menu = window.menuBar().addMenu("File")

    open_action = file_menu.addAction("Open PDF...")
    open_action.triggered.connect(window.open_pdf)

    save_action = file_menu.addAction("Save")
    save_action.setEnabled(False)

    save_as_action = file_menu.addAction("Save As...")
    save_as_action.triggered.connect(window.save_pdf_as)

    print_action = file_menu.addAction("Print PDF...")
    print_action.triggered.connect(window.print_pdf)


def setup_edit_menu(window):
    # * Create the Edit menu.

    edit_menu = window.menuBar().addMenu("Edit")

    add_content_action = edit_menu.addAction("Add Content")
    add_content_action.triggered.connect(window.add_content)

    edit_text_action = edit_menu.addAction("View/Edit Selected Text")
    edit_text_action.triggered.connect(window.view_edit_selected_text)

    delete_content_action = edit_menu.addAction("Delete Content Block")
    delete_content_action.triggered.connect(window.delete_selected_text)


def setup_view_menu(window):
    # * Create the View menu.

    view_menu = window.menuBar().addMenu("View")

    previous_action = view_menu.addAction("Previous Page")
    previous_action.triggered.connect(window.previous_page)

    next_action = view_menu.addAction("Next Page")
    next_action.triggered.connect(window.next_page)

    zoom_in_action = view_menu.addAction("Zoom In")
    zoom_in_action.triggered.connect(window.zoom_in)

    zoom_out_action = view_menu.addAction("Zoom Out")
    zoom_out_action.triggered.connect(window.zoom_out)

    close_action = view_menu.addAction("Close PDF")
    close_action.setShortcut("Esc")
    close_action.triggered.connect(window.close_pdf)

    reset_action = view_menu.addAction("Reset Document")
    reset_action.triggered.connect(window.reset_document)