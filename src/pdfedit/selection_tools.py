# * PDF content-selection helper functions.

import fitz


# * PDF text-selection helper functions.
def find_text_block_at_click(page, x, y):
    blocks = page.get_text("blocks")

    for block in blocks:
        x0, y0, x1, y1, text = block[:5]

        if x0 <= x <= x1 and y0 <= y <= y1:
            return {
                "type": "Text",
                "bounds": (x0, y0, x1, y1),
                "text": text.strip(),
            }

# * Find the image block located at the clicked PDF coordinates.
def find_image_block_at_click(page, x, y):
    images = page.get_images(full=True)

    for image in images:
        xref = image[0]
        image_rects = page.get_image_rects(xref)

        for image_rect in image_rects:
            if image_rect.x0 <= x <= image_rect.x1 and image_rect.y0 <= y <= image_rect.y1:
                return {
                    "type": "Image",
                    "xref": xref,
                    "bounds": (image_rect.x0, image_rect.y0, image_rect.x1, image_rect.y1),
                    "width": image_rect.width,
                    "height": image_rect.height,
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


# * Build the selected-image object used by the editor workflow.
def build_selected_image_block(page, x, y):
    return find_image_block_at_click(page, x, y)
# * Build a selected sub-region inside an image.

def build_selected_image_region(page, start_x, start_y, end_x, end_y):
    selected_image = find_image_block_at_click(page, start_x, start_y)
    if selected_image is None:
        return None

    image_x0, image_y0, image_x1, image_y1 = selected_image["bounds"]
    region_x0 = max(min(start_x, end_x), image_x0)
    region_y0 = max(min(start_y, end_y), image_y0)
    region_x1 = min(max(start_x, end_x), image_x1)
    region_y1 = min(max(start_y, end_y), image_y1)

    if region_x1 <= region_x0 or region_y1 <= region_y0:
        return None
    return {

        "type": "ImageRegion",
        "xref": selected_image["xref"],
        "image_bounds": selected_image["bounds"],

        "bounds": (
            region_x0,
            region_y0,
            region_x1,
            region_y1,
        ),
        "width": region_x1 - region_x0,
        "height": region_y1 - region_y0,
    }

# * Build the selected-content object used by the editor workflow.
def build_selected_content(page, x, y):
    selected_image = build_selected_image_block(page, x, y)
    if selected_image is not None:
        return selected_image
    return build_selected_text_block(page, x, y)