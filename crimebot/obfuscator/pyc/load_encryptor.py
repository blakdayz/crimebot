#load_encryptor
import pickle
from Cryptodome.Cipher import AES
import os
import base64

class LoadEncryptor:
    def __init__(self, key=None):
        self.key = key or os.urandom(16)

    @staticmethod
    def encrypt_code_object(code_data, key=None):
        if not key:
            key = LoadEncryptor().key

        cipher = AES.new(key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(pickle.dumps(code_data))
        return base64.b64encode(nonce + ciphertext + tag).decode()



