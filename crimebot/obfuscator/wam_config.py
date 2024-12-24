import os
from typing import Union, Dict

# Output directory for the final WAM provider files.
WAM_PROVIDER_OUTPUT_DIR: Union[str, None] = "dist"

# Path to the launcher source code (Go file).
LAUNCHER_SOURCE_PATH: Union[os.PathLike, None] = os.path.join(
    os.path.dirname(__file__), "launcher", "launcher.go"
)

# Path to the requirements file for installing required packages in the virtual environment.
REQUIREMENTS_FILE: Union[os.PathLike, None] = os.path.join(
    os.path.dirname(__file__), "requirements.txt"
)

PAYLOAD_NAME: Union[os.PathLike, None] = os.path.join(
    os.path.dirname(__file__), "payloads", "example2.txt"
)

# Mapping of environment variables and their default values. These can be overridden by user-defined
# environment variables at runtime.
ENV_VARS: Dict[str, Union[str, bool, int]] = {
    "WAM_OUTPUT_DIR": WAM_PROVIDER_OUTPUT_DIR,
    "LAUNCHER_SOURCE_PATH": LAUNCHER_SOURCE_PATH,
    "REQUIREMENTS_FILE": REQUIREMENTS_FILE,
}

if __name__ == "__main__":
    print(ENV_VARS)
