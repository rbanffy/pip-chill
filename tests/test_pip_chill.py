#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pip_chill
----------------------------------

Tests for `pip_chill` module.
"""


import sys
import unittest
# from contextlib import contextmanager
from click.testing import CliRunner

from pip_chill import pip_chill
from pip_chill import cli


class TestPip_chill(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_pip_ommitted(self):
        installed_packages = [
            package for (package, version) in pip_chill.chill()]
        for package in ['pip-chill', 'wheel', 'setuptools', 'pip']:
            assert package not in installed_packages

    def test_all(self):
        installed_packages = [
            package for (package, version) in pip_chill.chill(True)]
        for package in ['wheel', 'setuptools', 'pip']:
            assert package in installed_packages

    def test_command_line_interface_help(self):
        runner = CliRunner()
        result = runner.invoke(cli.main, ['--help'])
        assert result.exit_code == 0
        assert '--no-version  Omit version numbers' in result.output
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
        for package in ['wheel', 'setuptools', 'pip']:
            assert package in result.output

if __name__ == '__main__':
    sys.exit(unittest.main())
