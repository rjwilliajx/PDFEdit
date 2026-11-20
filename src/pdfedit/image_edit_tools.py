# * Image editing helper functions.
# * Replace the currently selected image while preserving its original bounds.
import fitz
from PIL import Image, ImageOps
from io import BytesIO
def replace_selected_image(
    document,
    page_number,
    selected_image,
    selected_image_region,
    replacement_path,
):

    if document is None:
        return False

    if selected_image is None:
        return False

    if selected_image.get("type") != "Image":
        return False

    if selected_image_region is None:
        return False

    if selected_image_region.get("type") != "ImageRegion":
        return False

    x0, y0, x1, y1 = selected_image_region["bounds"]
    image_rect = (x0, y0, x1, y1)

    print("Replace selected image called.")
    print(f"Original bounds: {selected_image['bounds']}")
    print(f"Original XREF: {selected_image['xref']}")
    print(f"Replacement file: {replacement_path}")
    print(f"Selected region bounds: {image_rect}")

    page = document.load_page(page_number)
    # Load the replacement and correct EXIF orientation.
    with Image.open(replacement_path) as source_image:
        replacement_image = ImageOps.exif_transpose(source_image)
        replacement_image = replacement_image.convert("RGB")

    # Calculate dimensions that fit inside the green selection.
    target_width = x1 - x0
    target_height = y1 - y0

    image_width, image_height = replacement_image.size

    scale = min(
        target_width / image_width,
        target_height / image_height,
    )

    scaled_width = image_width * scale
    scaled_height = image_height * scale

    # Center the replacement inside the selected region.
    left = x0 + (target_width - scaled_width) / 2
    top = y0 + (target_height - scaled_height) / 2

    replacement_rect = fitz.Rect(
        left,
        top,
        left + scaled_width,
        top + scaled_height,
    )

    # Encode the corrected image in memory.
    image_buffer = BytesIO()
    replacement_image.save(image_buffer, format="PNG")

    # Insert the corrected image.
    page = document.load_page(page_number)

    page.insert_image(
        replacement_rect,
        stream=image_buffer.getvalue(),
        keep_proportion=True,
    )

    return True