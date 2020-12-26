#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pip_chill
----------------------------------

Tests for `pip_chill` module.
"""


import os
import platform
import sys
import unittest

from pip_chill import cli, pip_chill
from pip_chill.pip_chill import Distribution

PIP_CHILL_CLI_FULL_PATH = cli.__file__
PYTHON_EXE_PATH = sys.executable
is_windows = any(platform.win32_ver())


class TestPip_chill(unittest.TestCase):
    def setUp(self):
        self.distribution_1 = Distribution("pip-chill", "2.0.0", [])
        self.distribution_2 = Distribution(
            "pip", "10.0.0", [self.distribution_1]
        )
        self.distribution_3 = Distribution(
            "pip", "11.0.0", [self.distribution_1]
        )

    def tearDown(self):
        pass

    def test_pip_ommitted(self):
        packages, _ = pip_chill.chill()
        hidden = {"wheel", "setuptools", "pip"}
        for package in packages:
            self.assertNotIn(package.name, hidden)

    def test_all(self):
        packages, _ = pip_chill.chill(True)
        package_names = {package.name for package in packages}
        for package in ["pip-chill", "pip"]:
            self.assertIn(package, package_names)

    def test_hashes(self):
        packages, _ = pip_chill.chill()
        for package in packages:
            self.assertEqual(hash(package), hash(package.name))

    def test_equality(self):
        self.assertNotEqual(self.distribution_1, self.distribution_2)
        self.assertEqual(self.distribution_1, self.distribution_1)
        self.assertEqual(self.distribution_2, self.distribution_3)
        self.assertEqual(self.distribution_2, self.distribution_2.name)

    def test_command_line_interface_help(self):
        argument = "--help"
        command = " ".join([PYTHON_EXE_PATH, PIP_CHILL_CLI_FULL_PATH, argument])

        returncode = os.system(command)
        self.assertEqual(returncode, 0)

        result = os.popen(command).read()
        self.assertIn("--no-version", result)
        self.assertIn("omit version numbers", result)
        self.assertIn("--help", result)
        self.assertIn("show this help message and exit", result)

    def test_command_line_interface_no_version(self):
        argument = "--no-version"
        command = " ".join([PYTHON_EXE_PATH, PIP_CHILL_CLI_FULL_PATH, argument])

        returncode = os.system(command)
        self.assertEqual(returncode, 0)

        result = os.popen(command).read()
        self.assertNotIn("==", result)

    def test_command_line_interface_verbose(self):
        argument = " --verbose"
        command = " ".join([PYTHON_EXE_PATH, PIP_CHILL_CLI_FULL_PATH, argument])

        returncode = os.system(command)
        self.assertEqual(returncode, 0)

        result = os.popen(command).read()
        self.assertIn("# Installed as dependency for", result)

    def test_command_line_interface_short_verbose(self):
        argument = "-v"
        command = " ".join([PYTHON_EXE_PATH, PIP_CHILL_CLI_FULL_PATH, argument])

        returncode = os.system(command)
        self.assertEqual(returncode, 0)

        result = os.popen(command).read()
        self.assertIn("# Installed as dependency for", result)

    def test_command_line_interface_verbose_no_version(self):
        argument = "--verbose --no-version"
        command = " ".join([PYTHON_EXE_PATH, PIP_CHILL_CLI_FULL_PATH, argument])

        returncode = os.system(command)
        self.assertEqual(returncode, 0)

        result = os.popen(command).read()
        self.assertNotIn("==", result)
        self.assertIn("# Installed as dependency for", result)

    def test_command_line_interface_omits_ignored(self):
        argument = ""
        command = " ".join([PYTHON_EXE_PATH, PIP_CHILL_CLI_FULL_PATH, argument])

        returncode = os.system(command)
        self.assertEqual(returncode, 0)

        result = os.popen(command).read()
        for package in ["wheel", "setuptools", "pip"]:
            self.assertFalse(
                any(p.startswith(package + "==") for p in result.split("\n"))
            )

    def test_command_line_interface_all(self):
        argument = "--all"
        command = " ".join([PYTHON_EXE_PATH, PIP_CHILL_CLI_FULL_PATH, argument])

        returncode = os.system(command)
        self.assertEqual(returncode, 0)

        result = os.popen(command).read()
        for package in ["pip-chill", "pip"]:
            self.assertIn(package, result)

    def test_command_line_interface_short_all(self):
        argument = "-a"
        command = " ".join([PYTHON_EXE_PATH, PIP_CHILL_CLI_FULL_PATH, argument])

        returncode = os.system(command)
        self.assertEqual(returncode, 0)

        result = os.popen(command).read()
        for package in ["pip-chill", "pip"]:
            self.assertIn(package, result)

    def test_command_line_interface_long_all(self):
        argument = "--show-all"
        command = " ".join([PYTHON_EXE_PATH, PIP_CHILL_CLI_FULL_PATH, argument])

        returncode = os.system(command)
        self.assertEqual(returncode, 0)

        result = os.popen(command).read()
        for package in ["pip-chill", "pip"]:
            self.assertIn(package, result)

    def test_command_line_invalid_option(self):
        argument = "--invalid-option"
        command = " ".join([PYTHON_EXE_PATH, PIP_CHILL_CLI_FULL_PATH, argument])

        returncode = os.system(command)

        if not is_windows:
            self.assertEqual(returncode, 512)
        else:
            self.assertEqual(returncode, 2)

    def test_command_line_interface_omit_self_on_request(self):
        argument = "--omit-self"
        command = " ".join([PYTHON_EXE_PATH, PIP_CHILL_CLI_FULL_PATH, argument])

        returncode = os.system(command)
        self.assertEqual(returncode, 0)

        result = os.popen(command).read()
        self.assertFalse(
            any(p.startswith("pip-chill" + "==") for p in result.split("\n"))
        )

    def test_command_line_interface_short_omit_self_on_request(self):
        argument = "-o"
        command = " ".join([PYTHON_EXE_PATH, PIP_CHILL_CLI_FULL_PATH, argument])

        returncode = os.system(command)
        self.assertEqual(returncode, 0)

        result = os.popen(command).read()
        self.assertFalse(
            any(p.startswith("pip-chill" + "==") for p in result.split("\n"))
        )

    def test_command_line_interface_doesnt_omit_self_by_default(self):
        argument = ""
        command = " ".join([PYTHON_EXE_PATH, PIP_CHILL_CLI_FULL_PATH, argument])

        returncode = os.system(command)
        self.assertEqual(returncode, 0)

        result = os.popen(command).read()
        self.assertTrue(
            any(p.startswith("pip-chill" + "==") for p in result.split("\n"))
        )


if __name__ == "__main__":
    sys.exit(unittest.main())
