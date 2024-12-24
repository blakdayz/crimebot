# load_encryptor
import logging
import pickle
from Cryptodome.Cipher import AES
import os
import base64

from tensorboardX.summary import image

from crimebot.obfuscator.pyc.generate_image import extract_randomkey_from_image


class LoadEncryptor:
    def __init__(self, key=None):
        self.key = key or os.urandom(16)

    @staticmethod
    def encrypt_code_object(
        code_data, image_key_path: os.PathLike = "../keys/key_image.png"
    ):
        key = ""
        try:
            key = extract_randomkey_from_image(image_key_path)
        except Exception as e:
            logging.error(e)
        finally:
            if not key:
                key = LoadEncryptor().key
            cipher = AES.new(key, AES.MODE_EAX)
            nonce = cipher.nonce
            ciphertext, tag = cipher.encrypt_and_digest(pickle.dumps(code_data))
            return base64.b64encode(nonce + ciphertext + tag).decode()


if __name__ == "__main__":
    cryptor = LoadEncryptor("../keys/key_image.png")
    print(cryptor.encrypt_code_object(pickle.dumps("print('Hello, World!')")))

    # Output: Encrypted code object as a base64 string
