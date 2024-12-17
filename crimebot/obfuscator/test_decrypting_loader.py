import logging

from PIL import Image

from crimebot.obfuscator.pyc.decrypting_loader import generate_image, obfuscate_pyc, register_loader, LoadEncryptor, DecryptingLoader



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
        key = cryptor.extract_key_from_image(img)
    except Exception as e:
        logging.error(f"Error extracting key from image: {e}")
        raise

    # Create an instance of DecryptingLoader with the extracted key
    loader = DecryptingLoader(image_path)
    loader.key = key

    # Register the loader
    sys.meta_path.insert(0, loader)

    # Import the obfuscated module


test_obfuscation("pyc/example2.pyc", "obfuscated_test_script.py", "key_image.png")