import argparse
import json
import logging
import os
from typing import List

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from src.file_handler import QuaternionFileHandler
from src.quaternion import Quaternion
from src.encryptor import QuaternionEncryptor
from src.encoder import QuaternionEncoder
from src.plotter import QuaternionPlotter


app = FastAPI()


class QuaternionRequest(BaseModel):
    key: str
    quaternions: List[dict]  # List of quaternion components


class QuaternionCLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Welcome to QET. The Quaternion Encryption Tool (Experimental), by Derek Hinch <derek.hinch@qompute.ai>. This software is not licensable."
        )

        # Define primary modes
        self.parser.add_argument(
            "mode",
            choices=["encrypt", "decrypt", "generate-key", "delete-key", "service"],
            help="Mode to run: encrypt, decrypt, generate-key, delete-key, service",
        )

        # Input and output options
        self.parser.add_argument(
            "input",
            type=str,
            nargs="?",
            help="The input message or path to file (optional for key management modes)",
        )
        self.parser.add_argument(
            "--key",
            type=str,
            help="Path to the key file",
            default="key_quaternion.json",
        )
        self.parser.add_argument(
            "--output",
            type=str,
            choices=["stdout", "json", "binary"],
            help="Output format",
            default="stdout",
        )
        self.parser.add_argument(
            "--file", action="store_true", help="Treat input as a file"
        )
        self.parser.add_argument(
            "--plot", action="store_true", help="Plot the quaternions"
        )
        self.parser.add_argument(
            "--binary", action="store_true", help="Use binary format for files"
        )
        self.parser.add_argument(
            "--host", type=str, default="127.0.0.1", help="Host for the FastAPI server"
        )
        self.parser.add_argument(
            "--port", type=int, default=8000, help="Port for the FastAPI server"
        )

    def run(self):
        args = self.parser.parse_args()

        if args.mode == "generate-key":
            self.generate_key(args)
        elif args.mode == "delete-key":
            self.delete_key(args)
        elif args.mode == "encrypt":
            key_data = self.load_key(args.key)
            self.encrypt_mode(args, key_data)
        elif args.mode == "decrypt":
            key_data = self.load_key(args.key)
            self.decrypt_mode(args, key_data)
        elif args.mode == "service":
            self.run_service(args.host, args.port)

    def generate_key(self, args):
        """Generate and save a new quaternion key."""
        key_data = QuaternionEncryptor.generate_and_save_key(args.key)
        print(f"Generated and saved key with GUID {key_data['guid']} to {args.key}")

    def delete_key(self, args):
        """Delete a saved key file."""
        if os.path.exists(args.key):
            os.remove(args.key)
            print(f"Key file {args.key} deleted.")
        else:
            print(f"Key file {args.key} not found.")

    def load_key(self, key_path):
        """Load a key from a file, generating it if it doesn't exist."""
        if not os.path.exists(key_path):
            print(f"Key file {key_path} not found. Generating a new key.")
            return QuaternionEncryptor.generate_and_save_key(key_path)
        else:
            with open(key_path, "r") as f:
                data = json.load(f)
            return {"guid": data["guid"], "key": Quaternion.from_dict(data["key"])}

    def encrypt_mode(self, args, key_data):
        """Encrypt the input data."""
        keys = key_data["keys"]

        # Process input
        if args.file:
            with open(args.input, "rb") as file:
                input_data = file.read()
            encoded_quaternions = QuaternionEncoder.encode_bytes_compact(input_data)
        else:
            input_data = args.input
            encoded_quaternions = QuaternionEncoder.encode_message_compact(input_data)

        # Encrypt the data using multiple keys
        encrypted_quaternions = QuaternionEncryptor.encrypt_quaternions(
            encoded_quaternions, keys
        )

        # Output results with GUID included
        self.output_results(encrypted_quaternions, key_data["guid"], args)

    @staticmethod
    def decrypt_mode(args, key_data):
        """Decrypt the input data."""
        keys = key_data["keys"]
        expected_guid = key_data["guid"]

        # Load the encrypted data
        if args.binary:
            decrypted_quaternions, guid = (
                QuaternionFileHandler.load_quaternions_from_binary(args.input)
            )
        else:
            with open(args.input, "r") as infile:
                data = json.load(infile)
            decrypted_quaternions = [
                Quaternion.from_dict(q) for q in data["quaternions"]
            ]
            guid = data["guid"]

        if guid != expected_guid:
            print(
                f"Warning: The GUID in the encrypted data ({guid}) does not match the key's GUID ({expected_guid})."
            )
            return

        # Decrypt the data using multiple keys
        decrypted_quaternions = QuaternionEncryptor.decrypt_quaternions(
            decrypted_quaternions, keys
        )

        # Convert to integer values for accurate decoding
        for q in decrypted_quaternions:
            q.round_components(0).threshold_zero()
            q._w = int(q.w)
            q._x = int(q.x)
            q._y = int(q.y)
            q._z = int(q.z)

        # Decode the data
        if args.file:
            decoded_data = QuaternionEncoder.decode_bytes_compact(decrypted_quaternions)
            with open(f"decrypted_output.bin", "wb") as file:
                file.write(decoded_data)
        else:
            decoded_data = QuaternionEncoder.decode_message_compact(
                decrypted_quaternions
            )
            print(f"Decoded Message: {decoded_data}")

    @staticmethod
    def output_results(quaternions, guid, args):
        """Output the encrypted/decrypted results, including the GUID."""
        output_data = {"guid": guid, "quaternions": [q.to_dict() for q in quaternions]}

        if args.output == "stdout":
            print(f"GUID: {guid}")
            print(f"Quaternions: {quaternions}")
        elif args.output == "json":
            with open("output.json", "w") as outfile:
                json.dump(output_data, outfile)
            print(f"Encrypted data saved to output.json with GUID: {guid}")
        elif args.output == "binary":
            QuaternionFileHandler.save_quaternions_to_binary(quaternions, "output.bin")
            with open("output.bin", "ab") as f:
                f.write(guid.encode())  # Append the GUID to the binary file
            print(f"Encrypted data saved to output.bin with GUID: {guid}")

    def run_service(self, host, port):
        """Run the FastAPI service mode."""
        uvicorn.run(app, host=host, port=port)


# FastAPI service endpoints
@app.post("/oracle/")
def oracle_operation(request: QuaternionRequest):
    key = Quaternion.from_dict(json.loads(request.key))
    quaternions = [Quaternion.from_dict(q) for q in request.quaternions]
    decrypted_quaternions = QuaternionEncryptor.decrypt_quaternions(quaternions, key)

    # Convert to integer values
    for q in decrypted_quaternions:
        q.round_components(0).threshold_zero()
        q._w = int(q.w)
        q._x = int(q.x)
        q._y = int(q.y)
        q._z = int(q.z)

    return {"decrypted_quaternions": [q.to_dict() for q in decrypted_quaternions]}


@app.post("/oracle/plot/")
def oracle_plot(request: QuaternionRequest):
    key = Quaternion.from_dict(json.loads(request.key))
    quaternions = [Quaternion.from_dict(q) for q in request.quaternions]
    decrypted_quaternions = QuaternionEncryptor.decrypt_quaternions(quaternions, key)

    # Convert to integer values
    for q in decrypted_quaternions:
        q.round_components(0).threshold_zero()
        q._w = int(q.w)
        q._x = int(q.x)
        q._y = int(q.y)
        q._z = int(q.z)

    QuaternionPlotter.plot_quaternions(
        decrypted_quaternions, title="Decrypted Quaternions"
    )
    return {"message": "Plot generated"}


@app.post("/oracle/encode/")
def oracle_encode(request: dict):
    message = request["message"]
    encoded_quaternions = QuaternionEncoder.encode_message_compact(message)
    return {"encoded_quaternions": [q.to_dict() for q in encoded_quaternions]}


@app.post("/oracle/decode/")
def oracle_decode(request: QuaternionRequest):
    quaternions = [Quaternion.from_dict(q) for q in request.quaternions]
    decoded_message = QuaternionEncoder.decode_message_compact(quaternions)
    return {"decoded_message": decoded_message}


@app.post("/oracle/encrypt/")
def oracle_encrypt(request: QuaternionRequest):
    key = Quaternion.from_dict(json.loads(request.key))
    quaternions = [Quaternion.from_dict(q) for q in request.quaternions]
    encrypted_quaternions = QuaternionEncryptor.encrypt_quaternions(quaternions, key)
    return {"encrypted_quaternions": [q.to_dict() for q in encrypted_quaternions]}


@app.post("/oracle/generate-key/")
def oracle_generate_key():
    key_data = QuaternionEncryptor.generate_key()
    return key_data


@app.post("/oracle/save-key/")
def oracle_save_key(request: dict):
    key = Quaternion.from_dict(request["key"])
    guid = request["guid"]
    QuaternionEncryptor.save_key(key, guid)
    return {"message": "Key saved"}


@app.post("/oracle/load-key/")
def oracle_load_key(request: dict):
    guid = request["guid"]
    key = QuaternionEncryptor.load_key(guid)
    return key


@app.post("/oracle/message/encrypt")
def oracle_simple_message(request: dict):
    message = request["message"]
    key = None
    if "key" in request:
        key = Quaternion.from_dict(request["key"])
    if len(message) % 4 != 0:
        message += " " * (4 - len(message) % 4)
    if key is None:
        key = Quaternion.generate_random_quaternion()
    encoded_quaternions = QuaternionEncoder.encode_message_compact(message)
    encrypted_quaternions = QuaternionEncryptor.encrypt_quaternions(
        encoded_quaternions, key
    )
    return {
        "encrypted_quaternions": [q.to_dict() for q in encrypted_quaternions],
        "key": key.to_dict(),
    }


@app.post("/oracle/message/decrypt")
def oracle_simple_message_decrypt(request: dict):
    key = Quaternion.from_dict(request["key"])
    quaternions = [Quaternion.from_dict(q) for q in request["quaternions"]]
    decrypted_quaternions = QuaternionEncryptor.decrypt_quaternions(quaternions, key)

    # Convert to integer values
    for q in decrypted_quaternions:
        q.round_components(0).threshold_zero()
        q._w = int(q.w)
        q._x = int(q.x)
        q._y = int(q.y)
        q._z = int(q.z)

    decoded_message = QuaternionEncoder.decode_message_compact(decrypted_quaternions)
    return {"decoded_message": decoded_message}


if __name__ == "__main__":
    cli = QuaternionCLI()
    cli.run()
