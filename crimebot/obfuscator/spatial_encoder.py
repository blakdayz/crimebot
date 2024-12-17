"""
This module contains the code responsible for encoding and decoding messages using quaternions.
"""

import struct
from quaternion import Quaternion


class QuaternionEncoder:
    @staticmethod
    def encode_message_compact(message):
        quaternions = []
        scale_factor = 10000  # Example scale factor to shift decimal points
        for i in range(0, len(message), 4):
            chars = message[i : i + 4].ljust(4, "\x00")
            w = ord(chars[0])
            x = ord(chars[1])
            y = ord(chars[2])
            z = ord(chars[3])
            quaternion = Quaternion(w, x, y, z)
            quaternions.append(quaternion.to_discrete(scale_factor))
        return quaternions

    @staticmethod
    def encode_bytes_compact(byte_data):
        quaternions = []
        scale_factor = 10000  # Example scale factor to shift decimal points
        for i in range(0, len(byte_data), 4):
            chunk = byte_data[i : i + 4].ljust(4, b"\x00")
            w, x, y, z = struct.unpack("BBBB", chunk)
            quaternion = Quaternion(w, x, y, z)
            quaternions.append(quaternion.to_discrete(scale_factor))
        return quaternions

    @staticmethod
    def decode_message_compact(quaternions):
        scale_factor = 10000
        message = []
        for q in quaternions:
            q.from_discrete(scale_factor)
            char1 = chr(int(q.w))
            char2 = chr(int(q.x))
            char3 = chr(int(q.y))
            char4 = chr(int(q.z))
            message.extend([char1, char2, char3, char4])
        return "".join(message).rstrip("\x00")

    @staticmethod
    def decode_bytes_compact(quaternions):
        scale_factor = 10000
        byte_data = bytearray()
        for q in quaternions:
            q.from_discrete(scale_factor)
            byte_data.extend(
                struct.pack("BBBB", int(q.w), int(q.x), int(q.y), int(q.z))
            )
        return bytes(byte_data).rstrip(b"\x00")


if __name__ == "__main__":
    # Test the encoder
    message = "Hello, World!"
    encoded_quaternions = QuaternionEncoder.encode_message_compact(message)
    decoded_message = QuaternionEncoder.decode_message_compact(encoded_quaternions)
    assert message == decoded_message, f"Decoded message: {decoded_message}"

    # Test the encoder with bytes
    byte_data = b"Hello, World!"
    encoded_quaternions = QuaternionEncoder.encode_bytes_compact(byte_data)
    decoded_byte_data = QuaternionEncoder.decode_bytes_compact(encoded_quaternions)
    assert byte_data == decoded_byte_data, f"Decoded byte data: {decoded_byte_data}"
    print("All tests passed!")
