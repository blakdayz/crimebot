from typing import List

from crimebot.hybrid_compute.quaternion import Quaternion


class QuaternionEncoder:
    @staticmethod
    def encode_message_compact(message: str) -> List[Quaternion]:
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
