# WAM (Weak Ass Malware [tm]): A Python-based ML controlled execution flow with Obfuscator/RSA String Encryptor and C2RAT with Golang Encrypted VFS Launcher 

Welcome to the WAM project, a powerful tool for obfuscating and encrypting Python pyc files while also providing remote access trojan (C2RAT) functionality. This README file will provide you with an overview of the entire codebase, its components, and how to use them.

## Overview

The WAM project consists of two main components: an obfuscator for Python pyc files and a C2RAT module with steganography and side-channel communication capabilities. Additionally, there is a Golang component that decrypts the modified pyc files so they can be executed by the Python interpreter.

### Obfuscator (Python)

The obfuscator is responsible for modifying the control flow, encrypting strings, and collecting runtime statistics from the modified pyc files. The collected data can then be used to train a machine learning model for further analysis. Here are the main methods of the Obfuscator class:

- `obfuscate_pyc(file_path)`: This method takes a pyc file path as input, modifies its control flow, encrypts strings using Fernet encryption, and returns the obfuscated file path.

- `collect_data(file_path)`: This method collects runtime statistics from the obfuscated pyc file by reading it byte by byte and appending it to a numpy array.

- `analyze_data(data)`: This method takes the collected data as input, trains an ML model (not implemented in this code), and returns predictions based on the data.

- `train_model()`: This method loads training data from multiple pyc files, trains the ML model using the data, and saves the trained model for future use.

- `modify_obfuscated_pyc(file_path)`: This method takes an already obfuscated pyc file, further modifies its control flow, encrypts any remaining strings, and returns the modified file path.

### C2RAT Module (Python)

The C2RAT module allows for remote execution of commands using a C2 server, steganography, and side-channel communication. Here are the main methods of the C2RAT class:

- `encode(command)`: This method encodes the given command, obfuscates it by encoding in base64, and stores it in multiple steganographic images and side-channel files for secure transmission to the C2 server.

- `decode()`: This method decodes the obfuscated payload from the steganographic images and side-channel files, reconstructs the original command, and returns it.

- `execute_command(command)`: This method sends the encoded command to the C2 server using HTTP POST requests and handles the response accordingly.

- `start_thread(command)`: This method starts a new thread with the given command and executes the `execute_command` method in that thread.

- `stop_thread(command)`: This method stops the execution of the given command by joining and killing the associated thread.

The C2RAT module also includes utility functions for opening a browser window with a specified URL, displaying a system screenshot after capturing it, and stopping the entire program.

### Golang Execution Engine w/PandorasBox VFS (Perfect Forward Secrecy)

The Golang component is responsible for decrypting the modified pyc files so they can be executed by the Python interpreter. It uses the Fernet encryption algorithm to decrypt the strings and a virtual file system (pandorasbox) to write the decrypted data into an output file. Here are the main methods of the Golang component:

- `main()`: This is the entry point for the Golang program. It takes the input obfuscated and encrypted pyc file path, the output desired pyc file path, and performs the decryption process using the provided encryption key.

## Usage



### Pyc Generation

To run the pyc operation we 

To use the WAM project, follow these steps:

1. Clone the repository or download the code.
2. Install any missing dependencies (e.g., Pillow for image manipulation, pandorasbox for Golang component).
3. Run the Python obfuscator script in a Python environment that supports threading and HTTP requests.
4. Obtain the modified pyc file from the output directory.
5. In a separate environment, run the Golang decryption component with the input and output file paths.
6. Use a Python interpreter to execute the decrypted pyc file in the output directory.
7. Interact with the C2RAT module by entering commands when prompted, or stop the program using the 'exit' command.


The WAM project aims to provide an effective combination of obfuscation, encryption, and remote access capabilities for Python pyc files. By leveraging advanced techniques like control flow modification and steganography, it offers a robust way to protect your codebase from reverse engineering efforts. The Golang component enables the execution of decrypted pyc files in a separate environment, further enhancing security measures.