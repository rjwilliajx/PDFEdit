import qrcode


def generate_qr_code(data: str, output_path: str = "temp_qr.png") -> str:
    """Generate a QR code image and return the saved file path."""

    if not data.strip():
        raise ValueError("QR code content cannot be empty.")

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=5,
        border=4,
    )

    qr.add_data(data.strip())
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)

    return output_path


# if __name__ == "__main__":
#     path = generate_qr_code("https://www.google.com")
#
#     print(f"QR code created: {path}")
