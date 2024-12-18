import base64
import logging
import sys
import pickle
import types

from Cryptodome.Cipher import AES
from PIL import Image

class DecryptingLoader:
    """
    Creates a loader for transparent encrypted module detection and decryption
    from a simple shared stego image key using sys.meta_path injection
    """
    def __init__(self, image_path):
        self.image_path = image_path
        self.key = None

    def find_spec(self, fullname, path=None, target=None):
        if fullname == "__main__":
            with open("__main__.py", "rb") as f:
                encrypted_code = f.read()
            return self._create_module_from_encrypted_code(encrypted_code)
        return None

    def _create_module_from_encrypted_code(self, encrypted_code):
        # Extract the key from the image
        if not self.key:
            with Image.open(self.image_path) as img:
                pixels = list(img.getdata())

            key_bytes = bytearray()
            for i in range(16):  # AES key size is 16 bytes
                pixel_index = i % len(pixels)
                r, g, b = pixels[pixel_index]
                byte_value = ((r & 1) << 7) | ((g & 1) << 6) | ((b & 1) << 5)
                key_bytes.append(byte_value)
            self.key = base64.b64decode(key_bytes).hex()

        # Decrypt the encrypted code object from the module's source
        encrypted_code_object = base64.b64decode(encrypted_code)

        try:
            cipher = AES.new(self.key, AES.MODE_EAX)
            nonce = encrypted_code_object[:16]
            ciphertext = encrypted_code_object[16:]
            tag = encrypted_code_object[-16:]
            decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
        except Exception as e:
            logging.error(f"Failed to decrypt code object: {e}")
            raise

        # Load the decrypted code object
        try:
            code = pickle.loads(decrypted_data)
        except Exception as e:
            logging.error(f"Failed to deserialize code object: {e}")
            raise

        # Execute the decrypted code object
        module = types.ModuleType("__main__")
        exec(code, module.__dict__)
        return module

    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]

        spec = self.find_spec(fullname)
        if spec is None:
            raise ImportError(f"No spec found for {fullname}")

        module = types.ModuleType(fullname)
        sys.modules[fullname] = module
        logging.debug("Module loaded: {}".format(fullname))
        return module
