# PyC Obfuscator

This project consists of a Python module and a Go program designed to obfuscate .pyc files. The goal is to make the original Python code unreadable and executable without additional tools, adding complexity for potential attackers.

## Features:
- **Obfuscation**: Modifies the control flow of bytecode instructions.
- **Encryption**: Encrypts string literals in the code to further hinder readability.
- **Execution Environment**: A Go program that executes the obfuscated .pyc file using Python.

## Installation:
1. Clone the repository.
2. Install dependencies for Python (e.g., `cryptography`).
3. Run the Go program to execute the obfuscated .pyc file.

## Usage:
- Place your Python script in the same directory as `example.py`.
- Run `python example.py` to generate a .pyc file.
- Use the provided Python script to obfuscate the .pyc file.
- Run `go run main.go` to execute the obfuscated .pyc file.


## UML Guide to How It Works