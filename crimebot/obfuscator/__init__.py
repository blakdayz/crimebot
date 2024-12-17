import random
import string
import uuid


class IndividualityProvider:

    @classmethod
    def generate_nano_id(self, length=10):
        if length < 1 or length > 256:
            raise ValueError("Length must be between 1 and 256")

        chars = string.ascii_uppercase + string.digits
        id = "".join(random.choice(chars) for _ in range(length))
        return id


if __name__ == "__main__":
    print(generate_nano_id())
