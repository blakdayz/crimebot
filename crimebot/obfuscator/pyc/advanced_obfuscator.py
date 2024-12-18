# advanced_obfuscator
import marshal
import dis
from Cryptodome.Cipher import AES
import base64
import os
import random


class AdvancedObfuscator:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.key = os.urandom(16)

    def encrypt_string(self, s):
        # AES encryption for strings
        cipher = AES.new(self.key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(s.encode())
        return base64.b64encode(nonce + ciphertext + tag).decode()

    def modify_code(self, code):
        code = list(code)

        # Modify control flow by adding a no-op (NOP) instruction at random positions
        nop_positions = [
            random.randint(0, len(code) - 1) for _ in range(len(code) // 10)
        ]
        for pos in nop_positions:
            code.insert(pos, dis.opmap["NOP"])

        # Add dummy jumps to control flow
        jump_instructions = [dis.opmap["JUMP_FORWARD"], dis.opmap["JUMP_ABSOLUTE"]]
        for i in range(10):
            code.append(random.choice(jump_instructions))
            code.append(random.randint(0, len(code)))

        # Duplicate random instructions
        duplicate_positions = [
            random.randint(0, len(code) - 1) for _ in range(len(code) // 20)
        ]
        for pos in duplicate_positions:
            code.insert(pos + 1, code[pos])

        return bytes(code)

    def rename_symbols(self, code):
        # Rename variables, functions, and classes
        new_names = {}

        if hasattr(code, "co_varnames"):
            new_names.update(
                {old: f"var_{i}" for i, old in enumerate(code.co_varnames)}
            )

        if hasattr(code, "co_names"):
            new_names.update({old: f"name_{i}" for i, old in enumerate(code.co_names)})

        if hasattr(code, "co_cellvars"):
            new_names.update(
                {old: f"cell_{i}" for i, old in enumerate(code.co_cellvars)}
            )

        if hasattr(code, "co_freevars"):
            new_names.update(
                {old: f"free_{i}" for i, old in enumerate(code.co_freevars)}
            )

        return code.replace(
            co_varnames=tuple(new_names.get(var, var) for var in code.co_varnames),
            co_names=tuple(new_names.get(name, name) for name in code.co_names),
            co_cellvars=tuple(new_names.get(cell, cell) for cell in code.co_cellvars),
            co_freevars=tuple(new_names.get(free, free) for free in code.co_freevars),
        )

    def encrypt_code_object(self, code):
        # Encrypt the entire code object
        cipher = AES.new(self.key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(marshal.dumps(code))
        return base64.b64encode(nonce + ciphertext + tag).decode()

    def obfuscate_pyc_file(self):
        with open(self.input_file, "rb") as f:
            magic = f.read(8)
            timestamp = f.read(4)
            size = f.read(4)
            code = marshal.load(f)

        # Modify the code object
        for const in code.co_consts:
            if isinstance(const, str):
                encrypted_str = self.encrypt_string(const)
                code = code.replace(co_consts=(encrypted_str,), where=const)

        modified_code = self.modify_code(code.co_code)
        obfuscated_code = marshal.dumps(modified_code)

        # Rename symbols
        code = self.rename_symbols(code)

        # Encrypt the entire code object
        encrypted_code_object = self.encrypt_code_object(code)

        with open(self.output_file, "wb") as f:
            f.write(magic)
            f.write(timestamp)
            f.write(size)
            f.write(base64.b64decode(encrypted_code_object))


if __name__ == "__main__":
    # Example usage
    input_pyc_path = "example.pyc"
    output_pyc_path = "obfuscated_example.pyc"
    obfuscator = AdvancedObfuscator(input_pyc_path, output_pyc_path)
    obfuscator.obfuscate_pyc_file()
