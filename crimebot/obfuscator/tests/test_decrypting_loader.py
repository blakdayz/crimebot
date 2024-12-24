import logging
import os
from os import write

from PIL import Image, ImageDraw

from crimebot.obfuscator.pyc.decrypting_loader import DecryptingLoader
from crimebot.obfuscator.pyc.encrypted_module import write_module, inject
from crimebot.obfuscator.pyc.generate_image import generate_image
from crimebot.obfuscator.pyc.load_encryptor import LoadEncryptor


def create_image_for_key(image_name_to_create: os.PathLike = "patriot3.png"):
    # Generate an image with the encryption key embedded
    try:

        generate_image(image_name_to_create)
        logging.info("Generated image")
    except Exception as e:
        logging.error(f"Error generating image: {e}")


def obfuscate_pyc(input_pyc, output_script, image_path):
    write_module(input_pyc, output_script, "key_image.jpg")


def register_loader(image_path):
    pass


def extract_key_from_image(img):
    pass


def test_obfuscation(input_pyc, output_script, image_path):
    """
    Tests the obfuscation process.

    :param input_pyc: Path to the input pyc file.
    :param output_script: Path to the output obfuscated script.
    :param image_path: Path to the image where the encryption key will be embedded.
    """
    generate_image(image_path)
    obfuscate_pyc(input_pyc, output_script, image_path)
    register_loader(image_path)

    # Load and execute the obfuscated script using the custom loader
    import sys

    cryptor = LoadEncryptor()

    # Extract the key from the image
    img = Image.open(image_path)
    try:
        key = extract_key_from_image(img)
    except Exception as e:
        logging.error(f"Error extracting key from image: {e}")
        raise

    # Create an instance of DecryptingLoader with the extracted key
    loader = DecryptingLoader(image_path)
    loader.key = key

    # Register the loader
    sys.meta_path.insert(0, loader)

    # Import the obfuscated module


if __name__ == "__main__":
    generate_image("testimg.png")

# test_obfuscation("pyc/example2.pyc", "obfuscated_test_script.py", "../key_image.png")
