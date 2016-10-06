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

    def test_000_pip_ommitted(self):
        self.assertNotIn('pip', pip_chill.chill())

    def test_command_line_interface(self):
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output


if __name__ == '__main__':
    sys.exit(unittest.main())
