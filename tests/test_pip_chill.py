#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pip_chill
----------------------------------

Tests for `pip_chill` module.
"""

import os

from pip_chill import pip_chill
from pip_chill.pip_chill import Distribution


def test_pip_ommitted() -> None:
    packages, _ = pip_chill.chill()
    hidden = {"wheel", "setuptools", "pip"}
    for package in packages:
        assert package.name not in hidden


def test_all() -> None:
    packages, _ = pip_chill.chill(show_all=True)
    package_names = {package.name for package in packages}
    for package in ["pip-chill", "pip"]:
        assert package in package_names


def test_hashes() -> None:
    packages, _ = pip_chill.chill()
    for package in packages:
        assert hash(package) == hash(package.name)


def test_equality() -> None:
    d1 = Distribution("pip-chill", "2.0.0", [])
    d2 = Distribution("pip", "10.0.0", [d1])
    d3 = Distribution("pip", "11.0.0", [d1])
    assert d1 != d2
    assert d1 == d1
    assert d2 == d3
    assert d2 == d2.name


def test_command_line_interface_help() -> None:
    command = "pip_chill/cli.py --help"

    returncode = os.system(command)
    assert returncode == 0

    result = os.popen(command).read()
    assert "--no-version" in result
    assert "omit version numbers" in result
    assert "--help" in result
    assert "show this help message and exit" in result


def test_command_line_interface_no_version() -> None:
    command = "pip_chill/cli.py --no-version"

    returncode = os.system(command)
    assert returncode == 0

    result = os.popen(command).read()
    assert "==" not in result


def test_command_line_interface_verbose() -> None:
    command = "pip_chill/cli.py --verbose"

    returncode = os.system(command)
    assert returncode == 0

    result = os.popen(command).read()
    assert "# Installed as dependency for" in result


def test_command_line_interface_short_verbose() -> None:
    command = "pip_chill/cli.py -v"

    returncode = os.system(command)
    assert returncode == 0

    result = os.popen(command).read()
    assert "# Installed as dependency for" in result


def test_command_line_interface_verbose_no_version() -> None:
    command = "pip_chill/cli.py --verbose --no-version"

    returncode = os.system(command)
    assert returncode == 0

    result = os.popen(command).read()
    assert "==" not in result
    assert "# Installed as dependency for" in result


def test_command_line_interface_omits_ignored() -> None:
    command = "pip_chill/cli.py"

    returncode = os.system(command)
    assert returncode == 0

    result = os.popen(command).read()
    for package in ["wheel", "setuptools", "pip"]:
        #     any(p.startswith(f"{package}==") for p in result.split("\n"))
        # )
        assert not any(p.startswith(f"{package}==") for p in result.split("\n"))


def test_command_line_interface_all() -> None:
    command = "pip_chill/cli.py --all"

    returncode = os.system(command)
    assert returncode == 0

    result = os.popen(command).read()
    for package in ["pip-chill", "pip"]:
        assert package in result


def test_command_line_interface_short_all() -> None:
    command = "pip_chill/cli.py -a"

    returncode = os.system(command)
    assert returncode == 0

    result = os.popen(command).read()
    for package in ["pip-chill", "pip"]:
        assert package in result


def test_command_line_interface_long_all() -> None:
    command = "pip_chill/cli.py --show-all"

    returncode = os.system(command)
    assert returncode == 0

    result = os.popen(command).read()
    for package in ["pip-chill", "pip"]:
        assert package in result


def test_command_line_interface_no_chill() -> None:
    command = "pip_chill/cli.py --no-chill"

    returncode = os.system(command)
    assert returncode == 0

    result = os.popen(command).read()
    assert "pip-chill" not in result


def test_command_line_invalid_option() -> None:
    command = "pip_chill/cli.py --invalid-option"

    returncode = os.system(command)
    assert returncode == 512


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
