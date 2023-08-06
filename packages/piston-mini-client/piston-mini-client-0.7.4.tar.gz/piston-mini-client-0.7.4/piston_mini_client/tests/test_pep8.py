import os
import subprocess
import unittest

import piston_mini_client


class PackagePep8TestCase(unittest.TestCase):

    packages = [piston_mini_client]
    exclude = ['socks.py']  # Leave 3rd party dep. alone.

    def test_all_code(self):
        res = 0
        py_files = []
        for package in self.packages:
            py_files.append(os.path.dirname(package.__file__))
        res += subprocess.call(
            ["pep8",
             "--repeat",
             "--exclude", "".join(self.exclude)] + py_files)
        self.assertEqual(res, 0)


if __name__ == "__main__":
    unittest.main()
