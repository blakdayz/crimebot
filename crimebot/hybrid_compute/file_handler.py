"""
This module provides a class to save and load quaternions to and from files.
"""
import marshal
from pydantic.v1 import BaseModel
import json
import logging
from typing import Any, List
from crimebot.obfuscator.pyc.decrypting_loader import generate_pyc, test_obfuscation
from crimebot.hybrid_computation.quanternion import Quaternion
from quaternion_encoder import QuaternionEncoder as qenc

class pyc_object(BaseModel):
    """
    Represents the structure of the pyc file
    """
    magic: bytes
    timestamp: bytes
    code: any
    def __init__(self, magic, timestamp, code, **data: any):
        super().__init__(**data)
        self.magic = magic
        self.timestamp = timestamp
        self.code = code

class QuaternionFile(BaseModel):
    """
    Represents a compact format of quaternionic values (scalar, imaginary, imaginary, imaginary)
    """
    magic:bytes
    file_bytes:bytes

    def get_magic(self):
        return b'3754ACFF'




class QuaternionFileHandler:
    """
    Performs basic .pyc file reading, and writing operations
    Read returns a struct that is [4] bytes for the
    """
    def __init__(self):
        self._encoder = qenc() # QuaternionEncoder


    def read_pyc(self, file_path:str)-> (bytes, bytes, any):
        """
    `   Reads a  pytc file and marshals the code object. This is a 'clean' function
        :param file_path: The pathg to the python compiled bytecode
        :return:
        """
        try:

            with open(file_path, "rb") as f:
                magic = f.read(4)
                timestamp = f.read(4)
                code = marshal.load(f)
            return magic, timestamp, code
        except FileNotFoundError as e:
            logging.error(f'Error during file handling: {e}')

    def write_pyc(self, file_path, magic, timestamp, code):
        """

        :param file_path:
        :param magic:
        :param timestamp:
        :param code:
        :return:
        """
        with open(file_path, "wb") as f:
            f.write(magic)
            f.write(timestamp)
            marshal.dump(code, f)

    def _encode_pyc(self, pycobject: pyc_object):
        """
        Uses the QuaternionEncoder to create an array of spatial encodings
        :param pycobject: pyc_object
        :return:
        """
        self._encoder.encode_message_compact(pycobject)

    def _decode_pyc(self, file_path):
        """
        Uses the QuaternionEncoder to decode the compact array back into a functional pyc object
        :param pycobject: pyc_object
        :return:
        """
        self._encoder
        self._encoder.decode_message_compact(pycobject)
    def create_model(self,magic, timestamp,code):
        """
        Creates a pyc model and return the pyc object type
        """
        pyc_object = pyc_object(magic=magic, timestamp=timestamp, code=code)
        return pyc_object


    @staticmethod
    def save_quaternion_to_file(quaternion, filename)->bool:
        """
        Save a quaternion to a file.
        :param quaternion:  The quaternion to save.
        :param filename: The file name to save the quaternion to.
        :return: True if successful, False if failure
        """
        try:
            with open(filename, "w") as f:
                json.dump(quaternion.to_dict(), f)
                return True
        except Exception as e:
            logging.error(f"Failed to save quaternion to file: {e}")
            return False


    @staticmethod
    def load_quaternion_from_file(filename: str)-> Any | None:
        """
        Load a quaternion from a file
        :param filename: The file name to load the quaternion from.
        :return: A quaternion object.
        """
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            return Quaternion.from_dict(data)
        except Exception as e:
            logging.error(f"Failed to load quaternion from file: {e}")
            return None

    @staticmethod
    def save_list_of_quaternions_to_file(quaternion_list: List[Quaternion], filename: str):
        """
        Save a list of quaternions to a file.
        :param quaternion_list: The list of quaternions to save.
        :param filename: The file name to save the quaternions to.
        :return: True if successful, False if failure
        """
        try:
            with open(filename, "w") as f:
                json.dump([q.to_dict() for q in quaternion_list], f)
                return True
        except Exception as e:
            logging.error(f"Failed to save quaternion list to file: {e}")
            return False

    @staticmethod
    def load_list_of_quaternions_from_file(filename: str)-> List[Quaternion] | None:
        """
        Load a list of quaternions from a file
        :param filename: The file name to load the quaternions from.
        :return: A list of quaternion objects.
        """
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            return [Quaternion.from_dict(q) for q in data]
        except Exception as e:
            logging.error(f"Failed to load quaternion list from file: {e}")
            return None

    @staticmethod
    def save_quaternions_to_binary(quaternions, filename):
        with open(filename, 'wb') as f:
            for q in quaternions:
                f.write(q.to_binary())
            # GUID will be added separately in `output_results` function

    @staticmethod
    def load_quaternions_from_binary(filename):
        quaternions = []
        with open(filename, 'rb') as f:
            while chunk := f.read(16):  # Each quaternion is 16 bytes (4 floats)
                if len(chunk) < 16:
                    guid = chunk.decode()  # Last part is the GUID
                    break
                quaternions.append(Quaternion.from_binary(chunk))
        return quaternions, guid

    @classmethod
    def save_quaternion_to_json(cls, key, key_path):
        with open(key_path, "w") as f:
            json.dump(key.to_dict(), f)

    @classmethod
    def save_quaternions_to_json(cls, encrypted_quaternions, param):
        """
        Save a list of quaternions to a json file.
        :param encrypted_quaternions:
        :param param:
        :return:
        """
        with open(param, "w") as f:
            json.dump([q.to_dict() for q in encrypted_quaternions], f)

    @staticmethod
    def load_quaternions_from_json(param):
        """
        Load a list of quaternions from a json file.
        :param param:
        :return:
        """
        quaternions = []
        with open(param, "r") as f:
            data = json.load(f)
        for q in data:
            quaternions.append(Quaternion.from_dict(q))
        return quaternions

    @staticmethod
    def load_quaternion_from_json(param):
        """
        Load a quaternion from a json file.
        :param param:
        :return:
        """
        try:
            with open(param, "r") as f:
                data = json.load(f)
            return Quaternion.from_dict(data)
        except FileNotFoundError as e:
            logging.error(f"Failed to load quaternion from json: {e}")
            logging.info("Generating a new random quaternion.")
            return Quaternion.generate_random_quaternion()









if __name__ == "__main__":
    input_clean = 'example2.py'
    output_pyc = 'pyc/example2.pyc'
    generate_pyc(input_clean, output_pyc)
    output_script = 'obfuscated_test_script.py'
    image_path = '../obfuscator/key_image.png'
    test_obfuscation(output_pyc, output_script, image_path)
