from abc import ABC, abstractmethod


class WAMBuilder(ABC):
    """
    An abstract base class (interface) that defines the contract for building a (not so) Weak Ass Malware Module (WAM)
    provider and its associated files.
    """

    @abstractmethod
    def build(self, output_dir: str) -> None:
        """
        Builds the WAM provider.

        Args:
            output_dir (str): The output directory for the final files.

        Raises:
            Exception: If any part of the build process fails.

        Returns:
            None
        """
        pass

    @abstractmethod
    def clean(self, output_dir: str) -> None:
        """
        Cleans up any temporary files generated during the build process, excluding the final output files in the 'dist' directory.

        Args:
            output_dir (str): The output directory containing the final output files.

        Raises:
            Exception: If there are any issues cleaning up files.

        Returns:
            None
        """
        pass
