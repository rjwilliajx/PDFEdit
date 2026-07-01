# * PDF text-selection helper functions.

import fitz


# * Find the text block located at the clicked PDF coordinates.
def find_text_block_at_click(page, x, y):
    blocks = page.get_text("blocks")

    for block in blocks:
        x0, y0, x1, y1, text = block[:5]

        if x0 <= x <= x1 and y0 <= y <= y1:
            return {
                "bounds": (x0, y0, x1, y1),
                "text": text.strip(),
            }

    return None


# * Extract font, color, and line-height metadata for a selected text block.
def extract_text_block_metadata(page, selected_block):
    if selected_block is None:
        return None

    x0, y0, x1, y1 = selected_block["bounds"]
    selected_rect = fitz.Rect(x0, y0, x1, y1)
    text_dict = page.get_text("dict")

    font_name = None
    font_size = None
    font_color = None
    line_y_positions = []

    for text_block in text_dict["blocks"]:
        if text_block.get("type") != 0:
            continue

        for line in text_block["lines"]:
            line_rect = fitz.Rect(line["bbox"])

            if line_rect.intersects(selected_rect):
                line_y_positions.append(round(line_rect.y0, 2))

            for span in line["spans"]:
                span_rect = fitz.Rect(span["bbox"])

                if span_rect.intersects(selected_rect) and font_name is None:
                    font_name = span["font"]
                    font_size = span["size"]
                    font_color = span["color"]

    detected_line_height = None
    if len(line_y_positions) > 1:
        line_y_positions = sorted(set(line_y_positions))
        detected_line_height = line_y_positions[1] - line_y_positions[0]

    return {
        "font_name": font_name,
        "font_size": font_size,
        "color": font_color,
        "line_height": detected_line_height,
    }


# * Build the selected-text object used by the editor workflow.
def build_selected_text_block(page, x, y):
    selected_block = find_text_block_at_click(page, x, y)

    if selected_block is None:
        return None

    metadata = extract_text_block_metadata(page, selected_block)

    if metadata is not None:
        selected_block.update(metadata)

    return selected_block