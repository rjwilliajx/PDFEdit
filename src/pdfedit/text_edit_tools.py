# * PDF text-editing helper functions.

import fitz

from font_tools import line_height_to_factor, pdf_color_to_rgb, resolve_insert_font


# * Normalize selected text before reinserting it into the PDF.
def normalize_replacement_text(text):
    return " ".join(text.split())


# * Find the smallest expanded rectangle that can fit replacement text.
def find_fitting_text_rect(document, page_number, selected_text_block, replacement_text):
    x0, y0, x1, y1 = selected_text_block["bounds"]
    original_rect = fitz.Rect(x0, y0, x1, y1)

    detected_font = selected_text_block["font_name"]
    insert_font_name = resolve_insert_font(detected_font)

    original_font_size = selected_text_block["font_size"]
    if original_font_size is None:
        original_font_size = 10

    line_height = selected_text_block["line_height"]
    line_height_factor = line_height_to_factor(line_height, original_font_size)

    color = selected_text_block["color"]
    rgb = pdf_color_to_rgb(color)

    chosen_rect = None
    chosen_result = None
    max_extra_height = 80
    expansion_step = 1

    for extra_height in range(0, max_extra_height + expansion_step, expansion_step):
        test_rect = fitz.Rect(x0, y0, x1, y1 + extra_height)
        test_document = fitz.open("pdf", document.write())
        test_page = test_document.load_page(page_number)

        test_result = test_page.insert_textbox(
            test_rect,
            replacement_text,
            fontsize=original_font_size,
            lineheight=line_height_factor,
            fontname=insert_font_name,
            color=rgb,
        )

        test_document.close()

        if test_result >= 0:
            chosen_rect = test_rect
            chosen_result = test_result
            break

    if chosen_rect is None:
        return None

    return {
        "original_rect": original_rect,
        "chosen_rect": chosen_rect,
        "insert_font_name": insert_font_name,
        "font_size": original_font_size,
        "line_height_factor": line_height_factor,
        "rgb": rgb,
        "test_result": chosen_result,
    }


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
    page.add_redact_annot(fit_result["original_rect"], fill=(1, 1, 1))
    page.apply_redactions()

    result = page.insert_textbox(
        fit_result["chosen_rect"],
        replacement_text,
        fontsize=fit_result["font_size"],
        lineheight=fit_result["line_height_factor"],
        fontname=fit_result["insert_font_name"],
        color=fit_result["rgb"],
    )

    print(f"Text inserted at original font size {fit_result['font_size']}.")
    print(f"Text block expanded by {fit_result['chosen_rect'].y1 - fit_result['original_rect'].y1:.2f} points.")
    print(f"Insert textbox result: {result}")

    return True


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
