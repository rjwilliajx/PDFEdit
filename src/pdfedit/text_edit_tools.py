# * PDF text-editing helper functions.

import fitz

from font_tools import line_height_to_factor, pdf_color_to_rgb, resolve_insert_font


# * Normalize text while preserving intentional line breaks.
def normalize_replacement_text(text):
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


# * Find the smallest expanded rectangle that can fit replacement text.
# * Dynamically size the replacement text rectangle.
def find_fitting_text_rect(document, page_number, selected_text_block, replacement_text):
    x0, y0, x1, y1 = selected_text_block["bounds"]
    original_rect = fitz.Rect(x0, y0, x1, y1)

    insert_font_name = resolve_insert_font(
        selected_text_block["font_name"]
    )

    font_size = selected_text_block["font_size"] or 10
    line_height_factor = 1.2
    rgb = pdf_color_to_rgb(selected_text_block["color"])

    page = document.load_page(page_number)

    # * Calculate available space on the page.
    max_width = page.rect.width - x0
    max_height = page.rect.height - y0

    if max_width <= 0 or max_height <= 0:
        return None

    # * Measure each line using the selected font and size.
    lines = replacement_text.split("\n")

    text_width = max(
        fitz.get_text_length(
            line,
            fontname=insert_font_name,
            fontsize=font_size,
        )
        for line in lines
    )

    # * Allow a small margin for font measurement differences.
    required_width = text_width + 2

    # * Wrap text if it exceeds the available page width.
    chosen_width = min(required_width, max_width)

    # * Calculate the initial text height.
    required_height = max(
        font_size * 1.5,
        len(lines) * font_size * line_height_factor,
    )

    test_height = min(required_height, max_height)

    # * Expand vertically until the replacement text fits.
    test_document = fitz.open("pdf", document.tobytes())

    try:
        test_page = test_document.load_page(page_number)

        while True:
            test_rect = fitz.Rect(
                x0,
                y0,
                x0 + chosen_width,
                y0 + test_height,
            )

            test_result = test_page.insert_textbox(
                test_rect,
                replacement_text,
                fontsize=font_size,
                lineheight=line_height_factor,
                fontname=insert_font_name,
                color=rgb,
            )

            if test_result >= 0:
                return {
                    "original_rect": original_rect,
                    "chosen_rect": test_rect,
                    "insert_font_name": insert_font_name,
                    "font_size": font_size,
                    "line_height_factor": line_height_factor,
                    "rgb": rgb,
                    "test_result": test_result,
                }

            if test_height >= max_height:
                return None

            test_height = min(
                test_height + max(1, -test_result),
                max_height,
            )

    finally:
        test_document.close()

# * Replace selected text while preserving detected formatting where possible.
def replace_selected_text(document, page_number, selected_text_block):
    if selected_text_block is None:
        return False

    replacement_text = normalize_replacement_text(selected_text_block["text"])
    fit_result = find_fitting_text_rect(
        document,
        page_number,
        selected_text_block,
        replacement_text,
    )

    if fit_result is None:
        print("Edited text is too large for the selected area. The text block could not be expanded enough to fit.")
        return False

    page = document.load_page(page_number)
    page.add_redact_annot(
        fit_result["original_rect"],
        fill=False,
    )
    page.apply_redactions(
        images=0,
        graphics=0,
        text=0,
    )

    result = page.insert_textbox(
        fit_result["chosen_rect"],
        replacement_text,
        fontsize=fit_result["font_size"],
        lineheight=fit_result["line_height_factor"],
        fontname=fit_result["insert_font_name"],
        color=fit_result["rgb"],
    )

    print(f"Text inserted at selected font size {fit_result['font_size']}.")
    print(f"Text block expanded by {fit_result['chosen_rect'].y1 - fit_result['original_rect'].y1:.2f} points.")
    print(f"Insert textbox result: {result}")

    return True

# * Reposition existing PDF text without modifying the original document.
def move_selected_text(document, page_number, selected_text_block, delta_x, delta_y):
    if selected_text_block is None:
        return None

    working_document = None

    try:
        working_document = fitz.open("pdf", document.tobytes())
        page = working_document.load_page(page_number)

        original_rect = fitz.Rect(selected_text_block["bounds"])

        destination_rect = original_rect + (
            delta_x,
            delta_y,
            delta_x,
            delta_y,
        )

        if not page.rect.contains(destination_rect):
            working_document.close()
            return None

        # * Capture original text spans and baseline positions.
        spans = []

        for block in page.get_text("dict")["blocks"]:
            if block.get("type") != 0:
                continue

            for line in block["lines"]:
                for span in line["spans"]:
                    span_rect = fitz.Rect(span["bbox"])

                    if original_rect.contains(span_rect):
                        if tuple(line["dir"]) != (1.0, 0.0):
                            working_document.close()
                            return None

                        spans.append(span)

        if not spans:
            working_document.close()
            return None

        # * Remove original text while preserving images and graphics.
        page.add_redact_annot(original_rect, fill=False)
        page.apply_redactions(
            images=0,
            graphics=0,
            text=0,
        )

        # * Reinsert each span using its original baseline.
        for span in spans:
            origin_x, origin_y = span["origin"]

            result = page.insert_text(
                (
                    origin_x + delta_x,
                    origin_y + delta_y,
                ),
                span["text"],
                fontname=resolve_insert_font(span["font"]),
                fontsize=span["size"],
                color=pdf_color_to_rgb(span["color"]),
            )

            if result <= 0:
                working_document.close()
                return None

        return working_document

    except Exception as error:
        if working_document is not None:
            working_document.close()

        print(f"Text repositioning failed: {error}")
        return None

# * Delete the selected content block by redacting it from the PDF.
def delete_content_block(document, page_number, selected_text_block):
    if selected_text_block is None:
        return False

    x0, y0, x1, y1 = selected_text_block["bounds"]
    original_rect = fitz.Rect(x0, y0, x1, y1)

    page = document.load_page(page_number)
    page.add_redact_annot(original_rect, fill=(1, 1, 1))
    page.apply_redactions()

    return True
