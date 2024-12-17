# test_example.py
import logging
import os
import subprocess
import tempfile


logging.basicConfig(level=logging.DEBUG, filename="test_build.log", filemode="a")


import unittest
from crimebot.obfuscator.wam_provider import WamProvider


class TestWamExecution(unittest.TestCase):
    def setUp(self):
        self.provider = WamProvider()

    def test_wam_execution(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = os.path.join(temp_dir, "myenv")
            output_tarball = os.path.join(temp_dir, "myenv.tar.gz")
            launcher_output = os.path.join(temp_dir, "launcher", "launcher")

            # Create the directory for the launcher binary
            os.makedirs(os.path.dirname(launcher_output), exist_ok=True)

            # Create a virtual environment
            self.provider.create_virtualenv(env_path)

            # Compile Python code to pyc files
            source_dir = os.path.join(os.path.dirname(__file__), '..', 'payloads')
            output_dir = os.path.join(env_path, 'lib', 'python3.12', 'site-packages', 'crimebot', 'payloads')
            self.provider.compile_python_code(source_dir, output_dir)

            # Create a tarball of the virtual environment
            self.provider.create_tarball(env_path, output_tarball)

            # Build the Go launcher
            launcher_source = os.path.join(os.path.dirname(__file__), '..', 'obfuscator', 'launcher', 'launcher.go')
            self.provider.build_launcher(launcher_source, launcher_output)

    def tearDown(self):
        self.provider.cleanup()


if __name__ == "__main__":
    unittest.main()
