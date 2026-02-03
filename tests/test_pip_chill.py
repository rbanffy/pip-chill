#!/usr/bin/env python

"""
test_pip_chill
----------------------------------

Tests for `pip_chill` module.
"""

import os
import sys
import unittest

from pip_chill import pip_chill
from pip_chill.pip_chill import Distribution


class TestPipChill(unittest.TestCase):
    def setUp(self) -> None:
        self.distribution_1 = Distribution("pip-chill", "2.0.0", [])
        self.distribution_2 = Distribution(
            "pip", "10.0.0", [self.distribution_1]
        )
        self.distribution_3 = Distribution(
            "pip", "11.0.0", [self.distribution_1]
        )

    def tearDown(self) -> None:
        pass

    def test_pip_omitted(self) -> None:
        packages, _ = pip_chill.chill()
        hidden = {"wheel", "setuptools", "pip"}
        for package in packages:
            self.assertNotIn(package.name, hidden)

    def test_all(self) -> None:
        packages, _ = pip_chill.chill(True)
        package_names = {package.name for package in packages}
        all_packages = [
            "pip-chill",
        ]
        for package in all_packages:
            self.assertIn(package, package_names)

    def test_hashes(self) -> None:
        packages, _ = pip_chill.chill()
        for package in packages:
            self.assertEqual(hash(package), hash(package.name))

    def test_equality(self) -> None:
        self.assertNotEqual(self.distribution_1, self.distribution_2)
        self.assertEqual(self.distribution_1, self.distribution_1)
        self.assertEqual(self.distribution_2, self.distribution_3)
        self.assertEqual(self.distribution_2, self.distribution_2.name)

    def test_command_line_interface_help(self) -> None:
        command = "pip_chill/cli.py --help"

        return_code = os.system(command)
        self.assertEqual(return_code, 0)

        result = os.popen(command).read()
        self.assertIn("--no-version", result)
        self.assertIn("omit version numbers", result)
        self.assertIn("--help", result)
        self.assertIn("show this help message and exit", result)

    def test_command_line_interface_no_version(self) -> None:
        command = "pip_chill/cli.py --no-version"

        return_code = os.system(command)
        self.assertEqual(return_code, 0)

        result = os.popen(command).read()
        self.assertNotIn("==", result)

    def test_command_line_interface_verbose(self):
        command = "pip_chill/cli.py --verbose"

        return_code = os.system(command)
        self.assertEqual(return_code, 0)

        result = os.popen(command).read()
        self.assertIn("# Installed as dependency for", result)

    def test_command_line_interface_short_verbose(self) -> None:
        command = "pip_chill/cli.py -v"

        return_code = os.system(command)
        self.assertEqual(return_code, 0)

        result = os.popen(command).read()
        self.assertIn("# Installed as dependency for", result)

    def test_command_line_interface_verbose_no_version(self) -> None:
        command = "pip_chill/cli.py --verbose --no-version"

        return_code = os.system(command)
        self.assertEqual(return_code, 0)

        result = os.popen(command).read()
        self.assertNotIn("==", result)
        self.assertIn("# Installed as dependency for", result)

    def test_command_line_interface_omits_ignored(self) -> None:
        command = "pip_chill/cli.py"

        return_code = os.system(command)
        self.assertEqual(return_code, 0)

        result = os.popen(command).read()
        for package in ["wheel", "setuptools", "pip"]:
            self.assertFalse(
                any(p.startswith(f"{package}==") for p in result.split("\n"))
            )

    def test_command_line_interface_all(self) -> None:
        command = "pip_chill/cli.py --all"

        return_code = os.system(command)
        self.assertEqual(return_code, 0)

        result = os.popen(command).read()
        for package in ["pip-chill", "pip"]:
            self.assertIn(package, result)

    def test_command_line_interface_short_all(self) -> None:
        command = "pip_chill/cli.py -a"

        return_code = os.system(command)
        self.assertEqual(return_code, 0)

        result = os.popen(command).read()
        for package in ["pip-chill", "pip"]:
            self.assertIn(package, result)

    def test_command_line_interface_long_all(self):
        command = "pip_chill/cli.py --show-all"

        return_code = os.system(command)
        self.assertEqual(return_code, 0)

        result = os.popen(command).read()
        for package in ["pip-chill", "pip"]:
            self.assertIn(package, result)

    def test_command_line_interface_no_chill(self) -> None:
        command = "pip_chill/cli.py --no-chill"

        return_code = os.system(command)
        self.assertEqual(return_code, 0)

        result = os.popen(command).read()
        self.assertNotIn("pip-chill", result)

    def test_command_line_invalid_option(self) -> None:
        command = "pip_chill/cli.py --invalid-option"

        return_code = os.system(command)
        self.assertEqual(return_code, 512)


if __name__ == "__main__":
    sys.exit(unittest.main())
