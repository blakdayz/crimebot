import os
import platform
import datetime

def get_log_file_path():
    """
    Returns the path for the log file in the user's home directory.
    """
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, f"system_info_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")

def write_system_info():
    """
    Writes system information to a log file located in the user's home directory.
    """
    with open(get_log_file_path(), "w") as f:
        f.write(f"System info:\n")
        f.write(f"OS: {platform.system()}\n")
        f.write(f"Release: {platform.release()}\n")
        f.write(f"Version: {platform.version()}\n")
        f.write(f"Machine: {platform.machine()}\n")

if __name__ == "__main__":
    write_system_info()
