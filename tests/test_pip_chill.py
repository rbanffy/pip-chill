#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pip_chill
----------------------------------

Tests for `pip_chill` module.
"""


import sys
import unittest

from click.testing import CliRunner

from pip_chill import cli, pip_chill
from pip_chill.pip_chill import Distribution


class TestPip_chill(unittest.TestCase):
    def setUp(self):
        self.distribution_1 = Distribution('pip-chill', '2.0.0', [])
        self.distribution_2 = Distribution(
            'pip', '10.0.0', [self.distribution_1]
        )
        self.distribution_3 = Distribution(
            'pip', '11.0.0', [self.distribution_1]
        )

    def tearDown(self):
        pass

    def test_pip_ommitted(self):
        packages, _ = pip_chill.chill()
        hidden = {'wheel', 'setuptools', 'pip'}
        for package in packages:
            self.assertNotIn(package.name, hidden)

    def test_all(self):
        packages, _ = pip_chill.chill(True)
        package_names = {package.name for package in packages}
        for package in ['pip-chill', 'pip']:
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

    # def test_command_line_interface_help(self):
    #     runner = CliRunner()
    #     result = runner.invoke(cli.main, ['--help'])
    #     self.assertEqual(result.exit_code, 0)
    #     self.assertIn('--no-version', result.output)
    #     self.assertIn('Omit version numbers', result.output)
    #     self.assertIn('--help', result.output)
    #     self.assertIn('Show this message and exit.', result.output)

    # def test_command_line_interface_no_version(self):
    #     runner = CliRunner()
    #     result = runner.invoke(cli.main, ['--no-version'])
    #     self.assertEqual(result.exit_code, 0)
    #     self.assertNotIn('==', result.output)

    # def test_command_line_interface_verbose(self):
    #     runner = CliRunner()
    #     result = runner.invoke(cli.main, ['--verbose'])
    #     self.assertEqual(result.exit_code, 0)
    #     self.assertIn('# Installed as dependency for', result.output)

    # def test_command_line_interface_verbose_no_version(self):
    #     runner = CliRunner()
    #     result = runner.invoke(cli.main, ['--verbose', '--no-version'])
    #     self.assertEqual(result.exit_code, 0)
    #     self.assertNotIn('==', result.output)
    #     self.assertIn('# Installed as dependency for', result.output)

    # def test_command_line_interface_omits_ignored(self):
    #     runner = CliRunner()
    #     result = runner.invoke(cli.main)
    #     self.assertEqual(result.exit_code, 0)
    #     for package in ['wheel', 'setuptools', 'pip']:
    #         self.assertFalse(
    #             any(
    #                 [
    #                     p.startswith(package + '==')
    #                     for p in result.output.split('\n')
    #                 ]
    #             )
    #         )

    # def test_command_line_interface_all(self):
    #     runner = CliRunner()
    #     result = runner.invoke(cli.main, ['--all'])
    #     self.assertEqual(result.exit_code, 0)
    #     for package in ['pip-chill', 'pip']:
    #         self.assertIn(package, result.output)


if __name__ == '__main__':
    sys.exit(unittest.main())
