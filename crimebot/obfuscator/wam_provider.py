import logging
import os
import subprocess
import sys
import tempfile
import tarfile
import unittest
from pathlib import Path


class WamProvider:
    """
    A class that provides methods for building and managing a WAM (WebAssembly Module) provider.

    Attributes:
        launcher_path (str): The path to the generated launcher script.
        output_dir (str): The directory where the final output will be placed.
    """

    def __init__(self, output_dir: str):
        """
        Initializes the WamProvider instance with an empty launcher path and output directory.

        Args:
            output_dir (str): The directory where the final output will be placed.

        Returns:
            None
        """
        self.launcher_path = os.path.join(output_dir, "launcher")
        self.output_dir = output_dir

    def create_virtualenv(self, env_path: str) -> None:
        """
        Creates a new virtual environment using the given path.

        Args:
            env_path (str): The path to the virtual environment.

        Raises:
            subprocess.CalledProcessError: If the virtual environment creation fails.

        Returns:
            None
        """
        try:
            # Create a virtual environment
            subprocess.run([sys.executable, "-m", "venv", env_path], check=True)

            # Install required packages using the virtual environment's Python executable
            pip_executable = Path(env_path) / "bin" / "pip"
            requirements_file = Path(os.path.dirname(__file__)) / "requirements.txt"
            subprocess.run([str(pip_executable), "install", "-r", str(requirements_file)], check=True)

        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to create virtual environment: {e}")

    def compile_python_code(self, source_dir: Path, output_dir: Path) -> None:
        """
        Compiles Python code in the given source directory and writes the compiled files to the given output directory.

        Args:
            source_dir (Path): The path to the source directory.
            output_dir (Path): The path to the output directory.

        Returns:
            None
        """
        try:
            # Compile Python code to pyc files
            for root, _, files in os.walk(source_dir):
                for file in files:
                    if file.endswith(".py"):
                        source_path = Path(root) / file
                        subprocess.run([sys.executable, "-m", "compileall", str(source_path.parent)], check=True)

        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to compile Python code: {e}")

    def create_tarball(self, env_path: str, output_path: str) -> None:
        """
        Creates a tarball of the virtual environment.

        Args:
            env_path (str): The path to the virtual environment.
            output_path (str): The path to the output tarball file.

        Returns:
            None
        """
        try:
            # Create a tarball of the virtual environment
            with tarfile.open(output_path, "w:gz") as tar:
                tar.add(env_path, arcname=os.path.basename(env_path))

        except tarfile.TarError as e:
            raise Exception(f"Failed to create tarball: {e}")

    def build_launcher(self) -> None:
        """
        Builds the WAM launcher script from the given source path and writes it to the output directory.

        Args:
            None

        Raises:
            subprocess.CalledProcessError: If the launcher build fails.

        Returns:
            None
        """
        try:
            # Change to the directory containing the launcher source
            os.chdir(os.path.dirname(self.launcher_source))

            # Fetch required Go modules and tidy up
            subprocess.run(["rm", "go.mod"], check=True)  # delete the current mod definition
            subprocess.run(["go", "mod", "init", "crimebot"], check=True)  # Initialize module if not already done
            subprocess.run(["go", "mod", "tidy"], check=True)  # Fetch all dependencies

            # Build the WAM launcher script using Go
            try:
                subprocess.run(["go", "build", "-o", os.path.join(self.output_dir, "launcher")])
            except subprocess.CalledProcessError as e:
                raise Exception(f"Failed to build WAM launcher: {e}")

        except FileNotFoundError as e:
            raise Exception(f"Launcher source file not found: {e}")

    def clean_up(self) -> None:
        """
        Removes the generated launcher executable and its associated files.

        Returns:
            None
        """
        try:
            # Remove the generated launcher executable and its associated files
            subprocess.run(["rm", "-rf", self.launcher_path])
        except Exception as e:
            logging.error(f"Failed to clean up: {e}")


class WAMTestExample(unittest.TestCase):
    def setUp(self) -> None:
        """
        Sets up the test environment by creating a new WamProvider instance and initializing it.

        Returns:
            None
        """
        self.provider = WamProvider("dist")
        logging.info("Setting up test environment")

    def test_wam_execution(self) -> None:
        """
        Tests the execution of the WAM provider.

        Raises:
            Exception: If any part of the test fails.

        Returns:
            None
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = os.path.join(temp_dir, "myenv")
            output_tarball = os.path.join(self.provider.output_dir, "myenv.tar.gz")

            # Create the directory for the launcher binary
            os.makedirs(os.path.dirname(self.provider.launcher_path), exist_ok=True)

            # Create a virtual environment
            self.provider.create_virtualenv(env_path)
            logging.info("Created virtual environment")

            # Compile Python code to pyc files
            source_dir = Path(__file__).parent / ".." / "payloads"
            output_dir = os.path.join(env_path, 'lib', 'python3.12', 'site-packages', 'crimebot', 'payloads')
            self.provider.compile_python_code(source_dir, output_dir)
            logging.info("Compiled Python code")

            # Create a tarball of the virtual environment
            self.provider.create_tarball(env_path, output_tarball)
            logging.info("Created tarball")

            # Build the WAM launcher script from the given source path and write it to the output directory
            launcher_source = Path(__file__).parent / ".." / "obfuscator" / "launcher" / "launcher.go"
            self.provider.build_launcher(launcher_source)
            logging.info("Built WAM launcher")

    def tearDown(self) -> None:
        """
        Cleans up the test environment by removing any generated files.

        Returns:
            None
        """
        try:
            # Remove the generated launcher executable and its associated files
            self.provider.clean_up()
        except Exception as e:
            logging.error(f"Failed to clean up: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename="test_build.log", filemode="a")
    logging.info("Starting tests")

    unittest.main()
