"""
Quaternion class for quaternion operations
"""
import json
import logging

import numpy as np


class Quaternion:
    """
    Class for representing quaternions and performing operations on them.
    """
    def __init__(self, w=0, x=0, y=0, z=0):
        """
        Initialize a quaternion.
        :param w: The scalar w component of the quaternion.
        :param x: The vectorized x component of the quaternion.
        :param y: The vectorized y component of the quaternion.
        :param z: The vectorized z component of the quaternion.
        """
        self._w: float = w
        self._x: float = x
        self._y: float = y
        self._z: float = z

    @property
    def w(self)->float:
        """
        Get the scalar w component of the quaternion.
        :return:  The scalar w component of the quaternion.
        """
        return self._w

    @property
    def x(self)->float:
        """
        Get the vectorized x component of the quaternion.
        :return: The vectorized x component of the quaternion.
        """
        return self._x

    @property
    def y(self)->float:
        """
        Get the vectorized y component of the quaternion.
        :return: The vectorized y component of the quaternion.
        """
        return self._y

    @property
    def z(self)->float:
        """
        Get the vectorized z component of the quaternion.
        :return: The vectorized z component of the quaternion.
        """
        return self._z

    def __mul__(self, other):
        if isinstance(other, Quaternion):
            return Quaternion( # type: ignore # noqa
                self._w * other.w
                - self._x * other.x
                - self._y * other.y
                - self._z * other.z,
                self._w * other.x
                + self._x * other.w
                + self._y * other.z
                - self._z * other.y,
                self._w * other.y
                - self._x * other.z
                + self._y * other.w
                + self._z * other.x,
                self._w * other.z
                + self._x * other.y
                - self._y * other.x
                + self._z * other.w,
            )
        else:
            return Quaternion(
                self._w * other, self._x * other, self._y * other, self._z * other
            )

    def conjugate(self)->"Quaternion":
        """
        Get the conjugate of the quaternion.
        :return:
        """
        return Quaternion(self._w, -self._x, -self._y, -self._z)

    def normalize(self)->"Quaternion":
        """
        Normalize the quaternion.
        :return:
        """
        norm = np.sqrt(self._w**2 + self._x**2 + self._y**2 + self._z**2)
        return Quaternion(
            self._w / norm, self._x / norm, self._y / norm, self._z / norm
        )

    def round_components(self, decimal_places=0)->"Quaternion":
        """
        Round the components of the quaternion.
        :param decimal_places: An integer number of decimal places to round to.
        :return: A quaternion with rounded components.
        """
        self._w = round(self._w, decimal_places)
        self._x = round(self._x, decimal_places)
        self._y = round(self._y, decimal_places)
        self._z = round(self._z, decimal_places)
        return self

    def threshold_zero(self, threshold=1e-10)->"Quaternion":
        """
        Threshold the quaternion components to zero if they are below a certain threshold.
        :param threshold:
        :return:
        """
        try:
            self._w = 0 if abs(self._w) < threshold else self._w
            self._x = 0 if abs(self._x) < threshold else self._x
            self._y = 0 if abs(self._y) < threshold else self._y
            self._z = 0 if abs(self._z) < threshold else self._z
            return self
        except Exception as e:
            logging.error(f"Thresholding failed: {e}")

    def to_dict(self):
        """
        Convert the quaternion to a dictionary.
        """
        return {"w": self._w, "x": self._x, "y": self._y, "z": self._z}

    @staticmethod
    def from_dict(data)->"Quaternion":
        """
        Create a quaternion from a dictionary.
        :param data:
        :return:
        """
        return Quaternion(data["w"], data["x"], data["y"], data["z"])

    def __repr__(self):
        """
        String representation of the quaternion.
        :return:
        """
        return f"Quaternion({self._w}, {self._x}, {self._y}, {self._z})"

    @classmethod
    def generate_random_quaternion(cls)->"Quaternion":
        """
        Generate a random quaternion.
        :return:
        """
        components = np.random.rand(4) - 0.5
        q = Quaternion(*components).normalize()
        return q

    @classmethod
    def from_binary(cls, chunk):
        """
        Create a quaternion from binary data.
        :param chunk: The binary data to create the quaternion from.
        :return: A quaternion object.
        """
        try:
            return cls(*np.frombuffer(chunk, dtype=np.float32))
        except Exception as e:
            logging.error(f"Failed to create quaternion from binary: {e}")
            return cls()

    @staticmethod
    def save_quaternion_to_file(quaternion, filename):
        with open(filename, "w") as f:
            json.dump(quaternion.to_dict(), f)

    @staticmethod
    def load_quaternion_from_file(filename):
        with open(filename, "r") as f:
            data = json.load(f)
        return Quaternion.from_dict(data).normalize()

    def to_discrete(self, scale_factor=10000):
        """
        Convert the quaternion to discrete space by scaling and rounding the components.
        """
        self._w = round(self._w * scale_factor)
        self._x = round(self._x * scale_factor)
        self._y = round(self._y * scale_factor)
        self._z = round(self._z * scale_factor)
        return self

    def from_discrete(self, scale_factor=10000):
        """
        Convert the quaternion back from discrete space by dividing by the scale factor.
        """
        self._w /= scale_factor
        self._x /= scale_factor
        self._y /= scale_factor
        self._z /= scale_factor
        return self

    def isclose(self, other, rel_tol=1e-9, atol=1e-9):
        """
        Check if the quaternion is close to another quaternion.
        """
        return (
            np.isclose(self._w, other._w, atol=atol)
            and np.isclose(self._x, other._x, atol=atol)
            and np.isclose(self._y, other._y, atol=atol)
            and np.isclose(self._z, other._z,atol=atol)
        )

    def __eq__(self, other):
        """
        Check if the quaternion is equal to another quaternion.
        """
        return (
            self._w == other._w
            and self._x == other._x
            and self._y == other._y
            and self._z == other._z
        )

    def __ne__(self, other):
        """
        Check if the quaternion is not equal to another quaternion.
        """
        return not self.__eq__(other)

    def __hash__(self):
        """
        Hash the quaternion.
        """
        return hash((self._w, self._x, self._y, self._z))



    def as_tuple(self)->tuple:
        """
        Get the quaternion components as a tuple.
        :return: A tuple of the quaternion components.
        """
        return self._w, self._x, self._y, self._z

