import os
import base64
import py_compile
import sys
import types
from typing import io

from Cryptodome.Cipher import AES
from PIL import Image

import marshal
import logging

logging.basicConfig(level=logging.DEBUG)


class LoadEncryptor:
    def __init__(self):
        self.key = os.urandom(16)  # Generate a random key for each instance

    @staticmethod
    def generate_pyc_from_py(src_py_path, output_path: str):
        """
        Generates a .pyc file from the given Python source file.

        :param src_py_path: Path to the source Python file.
        :param output_path: Output path for the .pyc file.
        """
        try:
            code = py_compile.compile(file=src_py_path, cfile=output_path, doraise=True)

            logging.info(f"Generated pyc file {code} to {output_path}")
            with open(output_path, "rb") as file:
                print("Dumping output file:")
                print(file.read().hex())
                print("End dump.")
                marshal_data = marshal.loads(file.read())
                logging.info("Direct loading worked.")
            try:
                logging.info("Marshal data now:")
                print("Marshal data now:")
                print(marshal_data.hex())
                marshal.loads(marshal_data)
                logging.debug("Code object correctly marshalled and deserialized")
            except Exception as e:
                logging.error(
                    f"Error during marshalling/deserializing code object: {e}"
                )
                raise
        except Exception as e:
            logging.error(f"Error generating pyc file: {e}")

    def encrypt_code_object(self, code_data):
        """
        Encrypts the serialized code object.

        :param code_data: Serialized code data.
        :return: Base64 encoded encrypted code string.
        """
        try:
            cipher = AES.new(self.key, AES.MODE_GCM)
            nonce = cipher.nonce
            ciphertext, tag = cipher.encrypt_and_digest(code_data)

            encrypted_bytes = nonce + ciphertext + tag
            encrypted_code = base64.b64encode(encrypted_bytes).decode("utf-8")

            logging.debug(f"Encrypted code: {encrypted_code}")

            return encrypted_code
        except Exception as e:
            logging.error(f"Error encrypting code object: {e}")
            raise

    def embed_key_in_image(self, img, key):
        """
        Embeds the encryption key into the image.

        :param img: The PIL Image object.
        :param key: The encryption key to embed.
        """
        width, height = img.size
        if len(key) > width * height:
            raise ValueError("Key is too large to be embedded in the image.")

        pixels = list(img.getdata())
        for i, byte in enumerate(key):
            r, g, b = pixels[i]
            # Embed the byte into the red channel (assuming 8-bit color depth)
            new_r = (r & ~0b111) | (byte >> 5)
            new_g = (g & ~0b11) | ((byte >> 3) & 0b11)
            new_b = (b & ~0b1) | ((byte >> 1) & 0b1)
            pixels[i] = (new_r, new_g, new_b)

        img.putdata(pixels)

    @staticmethod
    def extract_key_from_image(img):
        """
        Extracts the encryption key from the image.

        :param img: The PIL Image object.
        :return: The extracted encryption key.
        """
        width, height = img.size
        pixels = list(img.getdata())
        key = bytearray()

        for i in range(width * height):
            r, g, b = pixels[i]
            byte = ((r & 0b111) << 5) | ((g & 0b11) << 3) | ((b & 0b1) << 1)
            key.append(byte)

        return bytes(key)


class DecryptingLoader:
    def __init__(self, image_path):
        self.image_path = image_path
        self.key = None

    def find_spec(self, fullname, path, target=None):
        pass

    def create_module(self, spec):
        return None

    def find_source(self, fullname):
        if fullname == "obfuscated_test_script":
            return io.StringIO('__source__ = "{}"'.format(__source__))
        return None

    def exec_module(self, module):
        """
        Execute Module
        :param module:
        :return:
        """
        if not self.key:
            # Extract the key from the image
            with Image.open(self.image_path) as img:
                pixels = list(img.getdata())

            key_bytes = bytearray()
            for i in range(16):  # AES key size is 16 bytes
                pixel_index = i % len(pixels)
                r, g, b = pixels[pixel_index]
                byte_value = ((r & 1) << 7) | ((g & 1) << 6) | ((b & 1) << 5)
                key_bytes.append(byte_value)

            self.key = bytes(key_bytes)

        # Decrypt the encrypted code object from the module's source
        encrypted_code_object = base64.b64decode(module.source)

        try:
            cipher = AES.new(self.key, AES.MODE_EAX)
            nonce = encrypted_code_object[:16]
            ciphertext = encrypted_code_object[16:-16]
            tag = encrypted_code_object[-16:]
            decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
        except Exception as e:
            logging.error(f"Failed to decrypt code object: {e}")
            raise

        # Load the decrypted code object
        try:
            code = marshal.loads(decrypted_data)
        except Exception as e:
            logging.error(f"Failed to deserialize code object: {e}")
            raise

        # Execute the decrypted code object
        exec(code, module.__dict__)

    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]

        source_file = self.find_source(fullname)
        if not source_file:
            raise ImportError(f"No source found for {fullname}")

        module = types.ModuleType(fullname)
        exec(source_file.read(), module.__dict__)
        sys.modules[fullname] = module
        logging.debug("Module loaded: {}".format(fullname))
        return module


def generate_image(image_path: str):
    """
    Generates an image for key embedding.

    :param image_path: Path where the generated image will be saved.
    """
    width, height = 100, 100
    img = Image.new("RGB", (width, height), color="white")
    img.save(image_path)
    logging.info(f"Generated image saved to: {image_path}")


def generate_pyc(input_py, output_pyc):
    """
    Generates pyc from py

    :param input_py: Path to the source Python file.
    :param output_pyc: Output path for the .pyc file.
    """
    cryptor = LoadEncryptor()
    cryptor.generate_pyc_from_py(input_py, output_pyc)


def obfuscate_pyc(input_pyc, output_script, image_path):
    """
    Obfuscates a pyc file and saves it as a Python script.

    :param input_pyc: Path to the pyc file.
    :param output_script: Path where the obfuscated script will be saved.
    :param image_path: Path to the image with the embedded key.
    """
    cryptor = LoadEncryptor()

    # Read and deserialize the code object from the pyc file
    try:
        with open(input_pyc, "rb") as f:
            pyc_magic = f.read(4)
            pyc_timestamp = f.read(4)
            code_object_data = f.read()

        logging.debug(f"Read {len(code_object_data)} bytes from .pyc file")
    except Exception as e:
        logging.error(f"Error reading .pyc file: {e}")
        raise

    try:
        logging.debug(f"Data after initial read: {code_object_data}")
        code_object = marshal.loads(code_object_data)

    except Exception as e:
        logging.error(f"Error deserializing code object: {e}")
        raise

    # Encrypt the code object
    encrypted_code = cryptor.encrypt_code_object(marshal.dumps(code_object))

    # Embed the key in the image
    img = Image.open(image_path)
    try:
        cryptor.embed_key_in_image(img, cryptor.key)
    except Exception as e:
        logging.error(f"Error embedding key in image: {e}")
        raise

    img.save(image_path)

    # Write the obfuscated script
    with open(output_script, "w") as f:
        f.write("encrypted_code = '{}'\n".format(encrypted_code))
        f.write("# This is an obfuscated Python script.\n")
        f.write("# Please use the DecryptingLoader to run it.\n")


def register_loader(image_path):
    """
    Registers the custom loader with the image path.

    :param image_path: Path to the image with the embedded key.
    """
    import sys
    from crimebot.obfuscator.pyc.decrypting_loader import DecryptingLoader

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
    from crimebot.obfuscator.pyc.decrypting_loader import DecryptingLoader

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


if __name__ == "__main__":
    input_clean = "../payloads/example2.py"
    output_pyc = "../payloads/example2.pyc"
    generate_pyc(input_clean, output_pyc)
    output_script = "../outgoing/obfuscated_test_script.py"
    image_path = "key_image.png"
    test_obfuscation(output_pyc, output_script, image_path)
