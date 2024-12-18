from PIL import Image

def generate_image(image_path):
    # Create an image with a random key embedded in it
    img = Image.new("RGB", (100, 100), color="white")
    pixels = list(img.getdata())
    for i in range(16):  # AES key size is 16 bytes
        pixel_index = i % len(pixels)
        r, g, b = pixels[pixel_index]
        byte_value = ((r & 1) << 7) | ((g & 1) << 6) | ((b & 1) << 5)
        pixels[i] = (byte_value, g, b)
    img.putdata(pixels)
    return img



