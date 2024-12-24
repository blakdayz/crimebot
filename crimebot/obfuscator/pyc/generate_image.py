import os
from PIL import Image


def generate_random_key_image(image_path: os.PathLike = None):
    # Create an image with a random key embedded in it
    img = Image.new("RGB", (16, 16), color="white")
    pixels = list(img.getdata())
    bytes = os.urandom(16)  # Generate a random AES key

    for i, byte in enumerate(bytes):
        r = (byte & 0xFF0000) >> 16
        g = (byte & 0xFF00) >> 8
        b = byte & 0xFF
        pixels[i] = (r, g, b)

    img.putdata(pixels)
    if image_path:
        img.save(image_path, "png")
    return img, bytes


def extract_randomkey_from_image(image_path: os.PathLike):
    """
    Extracts the random key from the image
    :param image_path:
    :return:
    """
    img = Image.open(image_path)
    pixels = list(img.getdata())
    key = b""

    for pixel in pixels[:16]:  # Only process the first 16 pixels (4x4 grid)
        byte = min((pixel[0] << 16) | (pixel[1] << 8) | pixel[2], 0xFF)
        key += bytes([byte])

    return key


if __name__ == "__main__":
    img, key_bytes = generate_random_key_image("../keys/pyc.jpg")
    key = extract_randomkey_from_image("../keys/pyc.jpg")

    print("Generated Key: ", key_bytes.hex())
    print("Extracted Key: ", key.hex())
