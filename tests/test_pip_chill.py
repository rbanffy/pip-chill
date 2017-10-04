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

from pip_chill import pip_chill
from pip_chill import cli


class TestPip_chill(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_pip_ommitted(self):
        packages, _ = pip_chill.chill()
        hidden = {'pip-chill', 'wheel', 'setuptools', 'pip'}
        for package in packages:
            assert package.name not in hidden

    def test_all(self):
        packages, _ = pip_chill.chill(True)
        package_names = {package.name for package in packages}
        for package in ['wheel', 'pip']:
            assert package in package_names

    def test_command_line_interface_help(self):
        runner = CliRunner()
        result = runner.invoke(cli.main, ['--help'])
        assert result.exit_code == 0
        assert '--no-version' in result.output
        assert 'Omit version numbers' in result.output
        assert '--help' in result.output
        assert 'Show this message and exit.' in result.output

    def test_command_line_interface_no_version(self):
        runner = CliRunner()
        result = runner.invoke(cli.main, ['--no-version'])
        assert result.exit_code == 0
        assert '==' not in result.output

    def test_command_line_interface_omits_ignored(self):
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        for package in ['pip-chill', 'wheel', 'setuptools', 'pip']:
            assert package not in result.output

    def test_command_line_interface_all(self):
        runner = CliRunner()
        result = runner.invoke(cli.main, ['--all'])
        assert result.exit_code == 0
        for package in ['wheel', 'pip']:
            assert package in result.output


if __name__ == '__main__':
    sys.exit(unittest.main())
