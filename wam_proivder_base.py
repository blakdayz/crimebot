from abc import ABC, abstractmethod
import os

class WamProviderBase(ABC):
    """
    An abstract base class that defines the core functionality of a (not so) Weak Ass Malware Module (WAM) provider.

    """

    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    @abstractmethod
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
        pass

    @abstractmethod
    def compile_python_code(self, source_dir: os.PathLike, env_path: os.PathLike) -> None:
        """
        Compiles Python code in the given source directory and writes the compiled files to the given output directory.

        Args:
            source_dir (os.PathLike): The path to the source directory.
            env_path (os.PathLike): The path to the virtual environment directory.

        Returns:
            None
        """
        pass

    @abstractmethod
    def create_tarball(self, env_path: str, output_path: os.PathLike) -> None:
        """
        Creates a tarball of the virtual environment.

        Args:
            env_path (str): The path to the virtual environment.
            output_path (os.PathLike): The path to the output tarball file.

        Returns:
            None
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def clean_up(self, output_dir: str) -> None:
        """
        Removes the generated launcher executable and its associated files from the given output directory.

        Args:
            output_dir (str): The output directory containing the final output files.

        Raises:
            Exception: If there are any issues cleaning up files.

        Returns:
            None
        """
        pass
