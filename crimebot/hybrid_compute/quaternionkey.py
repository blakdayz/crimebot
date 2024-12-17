import json
import logging
import math

from quaternion import Quaternion


class QuaternionKey:
    def __init__(self, quaternions: list[Quaternion]):
        self.quaternions = quaternions

    def as_tuple(self):
        return [q.as_tuple() for q in self.quaternions]

    def conjugate(self):
        return QuaternionKey([q.conjugate() for q in self.quaternions])

    def entropy(self):
        # Calculate entropy for the entire key
        total_entropy = 0
        for q in self.quaternions:
            components = [abs(q.w), abs(q.x), abs(q.y), abs(q.z)]
            total = sum(components)
            probabilities = [c / total for c in components]
            total_entropy += -sum(p * math.log2(p) for p in probabilities if p > 0)
        return total_entropy

    def discretize(self, factor=10000, mode="uniform"):
        return QuaternionKey([q.to_discrete(factor) for q in self.quaternions])

    @staticmethod
    def load_key(filepath):
        quaternions = []
        with open(filepath, "r") as f:
            data = json.load(f)
            for q_data in data:
                quaternions.append(Quaternion.from_dict(q_data))
        return QuaternionKey(quaternions)

    def save_key(self, filepath):
        """
        Save the key to a file.
        :param filepath:  Path to the file.
        :return:  None
        """
        try:
            data = [q.to_dict() for q in self.quaternions]
            with open(filepath, "w") as f:
                json.dump(data, f)
        except Exception as e:
            logging.error(f"Failed to save key: {e}")

    def quantum_entropy(self)->float:
        """
        Calculate the quantum entropy of the key. This is a measure of the randomness of the key based on the
        probabilities of the components of each quaternion. A lower entropy indicates a less random key.
        High randomness is considered a value above 2.0.
        :return:
        """
        # Calculate quantum entropy for the entire key
        total_entropy = 0
        for q in self.quaternions:
            components = [abs(q.w), abs(q.x), abs(q.y), abs(q.z)]
            total = sum(components)
            probabilities = [c / total for c in components]
            total_entropy += -sum(p * math.log2(p) for p in probabilities if p > 0)
        return total_entropy