import json
import logging
import os
import uuid

from file_handler import QuaternionFileHandler
from quaternion import Quaternion


def generate_random_quaternion():
    """
    Generate a random quaternion.
    :return: A random quaternion.
    """
    return Quaternion.generate_random_quaternion()


class QuaternionEncryptor:
    """
    Class for encrypting and decrypting quaternions.
    """

    @staticmethod
    def encrypt_quaternions(quaternions, keys):
        """Encrypt quaternions using multiple keys."""
        if not isinstance(keys, list):
            keys = [keys]  # Ensure keys is a list, even if a single quaternion
        encrypted = []
        for i, q in enumerate(quaternions):
            key = keys[i % len(keys)]  # Cycle through the list of keys
            encrypted.append(q * key)
        return encrypted

    @staticmethod
    def decrypt_quaternions(quaternions, keys):
        """Decrypt quaternions using multiple keys."""
        if not isinstance(keys, list):
            keys = [keys]  # Ensure keys is a list, even if a single quaternion
        decrypted = []
        for i, q in enumerate(quaternions):
            key = keys[i % len(keys)].conjugate()  # Cycle through the list of keys
            decrypted.append(q * key)
        return decrypted

    @staticmethod
    def generate_key(num_quaternions=8):
        """Generate a list of random quaternion keys."""
        keys = [
            Quaternion.generate_random_quaternion().to_discrete()
            for _ in range(num_quaternions)
        ]
        guid = str(uuid.uuid4())
        return {"guid": guid, "keys": keys}

    @staticmethod
    def generate_and_save_key(key_path, num_quaternions=8):
        """Generate multiple keys, assign them a GUID, and save them to a file."""
        key_data = QuaternionEncryptor.generate_key(num_quaternions)
        with open(key_path, "w") as key_file:
            json.dump(
                {
                    "guid": key_data["guid"],
                    "keys": [key.to_dict() for key in key_data["keys"]],
                },
                key_file,
            )
        print(f"Generated and saved key with GUID {key_data['guid']} to {key_path}")
        return key_data["guid"]

    @classmethod
    def save_key(cls, key, guid):
        """
        Add a key to our json key database.
        If the GUID exists we return the GUID with False, otherwise we save the key and return the GUID with True.

        :param key: The key quaternion to save
        :param guid: The guid
        :return: A dictionary with the guid and a True if saved successfully
        """
        try:
            with open("keys.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}

        if guid in data:
            return {"guid": guid, "saved": False}

        data[guid] = key.to_dict()

        with open("keys.json", "w") as f:
            json.dump(data, f)

        return {"guid": guid, "saved": True}

    @classmethod
    def load_key(self, key_path):
        """Load a key from a file, ensuring it is a list of quaternions."""
        if not os.path.exists(key_path):
            print(f"Key file {key_path} not found. Generating a new key.")
            return QuaternionEncryptor.generate_and_save_key(key_path)
        else:
            with open(key_path, "r") as f:
                data = json.load(f)
            keys = [Quaternion.from_dict(k) for k in data["keys"]]
            return {"guid": data["guid"], "keys": keys}


if __name__ == "__main__":
    # Test the encryptor
    quaternions = [generate_random_quaternion() for _ in range(5)]
    key = generate_random_quaternion()
    encrypted_quaternions = QuaternionEncryptor.encrypt_quaternions(quaternions, key)
    decrypted_quaternions = QuaternionEncryptor.decrypt_quaternions(
        encrypted_quaternions, key
    )

    print("Original quaternions:")
    for q in quaternions:
        print(q)

    print("\nEncrypted quaternions:")
    for q in encrypted_quaternions:
        print(q)

    print("\nDecrypted quaternions:")
    for q in decrypted_quaternions:
        print(q)
    atol = 1e-10
    # Check that the decrypted quaternions match the original quaternions within a tolerance
    for q1, q2 in zip(quaternions, decrypted_quaternions):
        assert q1.isclose(
            q2, atol=atol
        ), f"Decrypted quaternion {q2} does not match original quaternion {q1}"
