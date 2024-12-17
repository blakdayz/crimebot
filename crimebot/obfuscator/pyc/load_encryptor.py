import marshal

from Crypto.Cipher import AES
import base64
import os
from PIL import Image
import io


class LoadEncryptor:
    def __init__(self, key=None):
        self.key = key or os.urandom(16)

    def encrypt_code_object(self, code):
        cipher = AES.new(self.key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(marshal.dumps(code))
        return base64.b64encode(nonce + ciphertext + tag).decode()

    def embed_key_in_image(self, image_path, key):
        with Image.open(image_path) as img:
            pixels = list(img.getdata())

        # Convert the key to bytes
        key_bytes = base64.b64encode(key).decode()

        # Embed the key into the image (simplified example)
        for i in range(len(key_bytes)):
            pixel_index = i % len(pixels)
            r, g, b = pixels[pixel_index]
            new_r = (r & 0xFE) | ((ord(key_bytes[i]) >> 7) & 1)
            new_g = (g & 0xFE) | ((ord(key_bytes[i]) >> 6) & 1)
            new_b = (b & 0xFE) | ((ord(key_bytes[i]) >> 5) & 1)
            pixels[pixel_index] = (new_r, new_g, new_b)

        img.putdata(pixels)
        return img

    def extract_key_from_image(self, image_path):
        with Image.open(image_path) as img:
            pixels = list(img.getdata())

        key_bytes = bytearray()
        for i in range(len(key_bytes), 16):  # AES key size is 16 bytes
            pixel_index = i % len(pixels)
            r, g, b = pixels[pixel_index]
            byte_value = ((r & 1) << 7) | ((g & 1) << 6) | ((b & 1) << 5)
            key_bytes.append(byte_value)

        return base64.b64decode(key_bytes).hex()



if __name__ == '__main__':
    # Example usage of LoadEncryptor
    encryptor = LoadEncryptor()
    with open('example.pyc', 'rb') as f:
        magic = f.read(8)
        timestamp = f.read(4)
        size = f.read(4)
        code_object = marshal.load(f)

    encrypted_code_object = encryptor.encrypt_code_object(code_object)
    img_with_key = encryptor.embed_key_in_image('key_image.jpg', encryptor.key)
    img_with_key.save('obfuscated_key_image.jpg')
