import logging
import os
import pathlib
import tempfile

logging.basicConfig(level=logging.DEBUG, filename="../test_build.log", filemode="a")

import unittest
from crimebot.obfuscator.wam_provider import WamProvider, WAM_PROVIDER_OUTPUT_DIR, LAUNCHER_SOURCE_PATH

class TestWamExecution(unittest.TestCase):
    def setUp(self):
        self.provider = WamProvider(WAM_PROVIDER_OUTPUT_DIR)

    def test_wam_execution(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = os.path.join(temp_dir, "myenv")
            output_tarball = os.path.join(temp_dir, "myenv.tar.gz")
            launcher_output = os.path.join(temp_dir, "launcher", "launcher")

            # Create the directory for the launcher binary
            os.makedirs(os.path.dirname(launcher_output), exist_ok=True)

            # Create a virtual environment
            self.provider.create_virtualenv(env_path)
            logging.info("Created virtual environment")

            # Compile Python code to pyc files
            source_dir = pathlib.Path(__file__).parent / "payloads"
            output_dir = os.path.join(env_path, 'lib', 'python3.12', 'site-packages', 'crimebot', 'payloads')
            self.provider.compile_python_code(source_dir, output_dir)
            logging.info("Compiled Python code")

            # Create a tarball of the virtual environment
            self.provider.create_tarball(env_path, pathlib.Path(output_tarball))
            logging.info("Created tarball")

            # Build the Go launcher
            self.provider.build()
            logging.info("Built WAM launcher")

            # Arm the detonator (build, encrypt, embed, and move binary)
            self.provider.arm()
            logging.info("Armed detonator")

    def tearDown(self):
        ## Clean up artifacts created during testing
        #self.provider.wipe_custom_artifacts(WAM_PROVIDER_OUTPUT_DIR)
        pass
if __name__ == "__main__":
    unittest.main()
