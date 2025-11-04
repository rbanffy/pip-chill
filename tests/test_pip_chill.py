#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pip_chill
----------------------------------

Tests for `pip_chill` module.
"""

import os
import re
import sys
import unittest
import warnings
from typing import Optional

from pip_chill import pip_chill
from pip_chill.pip_chill import (
    Distribution,
    extract_name_extras,
    fallback_extract_name_extras,
    rgx_extras,
    rgx_operator,
    rgx_req_line,
    rgx_version,
    rgx_version_list,
)

TEST_REQUIREMENTS = [
    ("requests", "requests", False),
    ("requests>=2.0", "requests", False),
    ("requests[security]", "requests[security]", False),
    ("requests[security,tests]", "requests[security,tests]", False),
    ("requests[security,tests]>=2.0", "requests[security,tests]", False),
    ("requests[security, tests]>=2.0", "requests[security,tests]", False),
    ("requests[tests,security]>=2.0", "requests[security,tests]", False),
    ("bar[dev]; python_version<'3.10'", "bar[dev]", False),
    ("bar[foo,dev]; python_version<'3.10'", "bar[dev,foo]", False),
    ("bar[foo, dev]; python_version<'3.10'", "bar[dev,foo]", False),
    ("bar[dev]>2; python_version<'3.10'", "bar[dev]", False),
    ("bar[foo,dev]>=2; python_version<'3.10'", "bar[dev,foo]", False),
    ("bar[foo, dev]~=2; python_version<'3.10'", "bar[dev,foo]", False),
    ("foo; sys_platform=='win32'", "foo", False),
    ("foo[extra]; python_version<'3.10'", "foo[extra]", False),
    (
        "complex-package[extra1,extra2]>=1.0,<2.0; os_name=='posix'",
        "complex-package[extra1,extra2]",
        False,
    ),
    (
        "complex-package[extra1, extra2]>=1.0,<2.0; os_name=='posix'",
        "complex-package[extra1,extra2]",
        False,
    ),
    ('build ; extra == "dev"', "build", False),
    ('bump >= 1.3.2 ; extra == "dev"', "bump", False),
    ('id[test ,lint]; extra == "dev"', "id[lint,test]", False),
    ('id[test , lint] ; extra == "dev"', "id[lint,test]", False),
    ('bandit ; extra == "lint"', "bandit", False),
    ('interrogate ; extra == "lint"', "interrogate", False),
    ('mypy ; extra == "lint"', "mypy", False),
    ('ruff < 0.8.2 ; extra == "lint"', "ruff", False),
    ('types-requests ; extra == "lint"', "types-requests", False),
    ('pytest ; extra == "test"', "pytest", False),
    ('pytest-cov ; extra == "test"', "pytest-cov", False),
    ('pretend ; extra == "test"', "pretend", False),
    ('coverage[toml] ; extra == "test"', "coverage[toml]", False),
    ("invalid package string", "invalid package string", True),
    ("", "", True),  # empty string
    (" ; python_version<'3.10'", " ; python_version<'3.10'", True),  # only marker
]


class TestPip_chill(unittest.TestCase):
    def setUp(self):
        self.distribution_1 = Distribution("pip-chill", "2.0.0", [])
        self.distribution_2 = Distribution("pip", "10.0.0", [self.distribution_1])
        self.distribution_3 = Distribution("pip", "11.0.0", [self.distribution_1])

    def tearDown(self):
        pass

    def test_pip_ommitted(self):
        packages, _ = pip_chill.chill()
        hidden = {"wheel", "setuptools", "pip"}
        for package in packages:
            self.assertNotIn(package.name, hidden)

    def test_all(self):
        packages, _ = pip_chill.chill(show_all=True)
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

    def _run_cli(self, args: Optional[str] = None):
        command = f"pip_chill/cli.py {args}" if args else "pip_chill/cli.py"

        returncode = os.system(command)
        self.assertEqual(returncode, 0)

        with os.popen(command) as pipe:
            result = pipe.read()
        return result

    def test_command_line_interface_help(self):
        result = self._run_cli("--help")
        self.assertIn("--no-version", result)
        self.assertIn("omit version numbers", result)
        self.assertIn("--help", result)
        self.assertIn("show this help message and exit", result)

    def test_command_line_interface_no_version(self):
        result = self._run_cli("--no-version")
        self.assertNotIn("==", result)

    def test_command_line_interface_verbose(self):
        result = self._run_cli("--verbose")
        self.assertIn("# Installed as dependency for", result)

    def test_command_line_interface_short_verbose(self):
        result = self._run_cli("-v")
        self.assertIn("# Installed as dependency for", result)

    def test_command_line_interface_verbose_no_version(self):
        result = self._run_cli("--verbose --no-version")
        self.assertNotIn("==", result)
        self.assertIn("# Installed as dependency for", result)

    def test_command_line_interface_omits_ignored(self):
        result = self._run_cli()
        for package in ["wheel", "setuptools", "pip"]:
            self.assertFalse(any(p.startswith(f"{package}==") for p in result.splitlines()))

    def test_command_line_interface_all(self):
        result = self._run_cli("--all")
        for package in ["pip-chill", "pip"]:
            self.assertIn(package, result)

    def test_command_line_interface_short_all(self):
        result = self._run_cli("-a")
        for package in ["pip-chill", "pip"]:
            self.assertIn(package, result)

    def test_command_line_interface_long_all(self):
        result = self._run_cli("--show-all")
        for package in ["pip-chill", "pip"]:
            self.assertIn(package, result)

    def test_command_line_interface_no_chill(self):
        result = self._run_cli("--no-chill")
        self.assertNotIn("pip-chill", result)

    def test_command_line_invalid_option(self):
        command = "pip_chill/cli.py --invalid-option"
        returncode = os.system(command)
        self.assertEqual(returncode, 512)

    def test_regex(self):
        assert re.match(rgx_operator, "==")
        assert re.match(rgx_operator, ">")
        assert re.match(rgx_version, ">2")
        assert re.match(rgx_version_list, ">2.4")
        assert re.match(rgx_version_list, ">2.3.4")
        assert re.match(rgx_version_list, ">=2.3.4, <4")
        assert re.match(rgx_version_list, "")
        assert re.match(rgx_extras, "[>=2.3.4]")
        assert re.match(rgx_req_line, "requests[extras]")
        assert re.match(rgx_req_line, "requests[extra1,extra2]")
        assert re.match(rgx_req_line, "requests[extra1, extra2]")
        assert re.match(rgx_req_line, "requests>2.6")
        assert re.match(rgx_req_line, "requests[extra]>=2")
        assert re.match(rgx_req_line, "bar[foo, dev]~=2; python_version<'3.10'")
        assert re.match(
            rgx_req_line, "bar[foo, dev]~=2; python_version<'3.10' # My needless comment"
        )
        assert re.match(rgx_req_line, "bump >= 1.3.2")
        assert not re.match(rgx_req_line, "invalid package string")

    def test_fallback_extract_name_extras(self):
        for req_string, expected, should_warn in TEST_REQUIREMENTS:
            with self.subTest(req=req_string):
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    result = fallback_extract_name_extras(req_string)

                    self.assertEqual(result, expected, f"Failed for: {req_string!r}")

                    if should_warn:
                        self.assertTrue(
                            any("Invalid" in str(warning.message) for warning in w),
                            f"Expected warning for {req_string!r}",
                        )
                    else:
                        self.assertFalse(
                            any("Invalid" in str(warning.message) for warning in w),
                            f"Unexpected warning for {req_string!r}",
                        )

    def test_extract_name_extras(self):
        for req_string, expected, should_warn in TEST_REQUIREMENTS:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                result = extract_name_extras(req_string)

                self.assertEqual(result, expected, f"Failed for: {req_string!r}")

                if should_warn:
                    self.assertTrue(
                        any("Invalid" in str(warning.message) for warning in w),
                        f"Expected warning for {req_string!r}",
                    )
                else:
                    self.assertFalse(
                        any("Invalid" in str(warning.message) for warning in w),
                        f"Unexpected warning for {req_string!r}",
                    )

    def test_distribution_str_and_name_without_version(self):
        dist_top = Distribution("foo", "1.2.3")
        dist_dep = Distribution("bar", "2.0", required_by={"foo"})

        self.assertEqual(str(dist_top), "foo==1.2.3")
        self.assertEqual(dist_top.get_name_without_version(), "foo")

        self.assertIn("bar", str(dist_dep))
        self.assertIn("Installed as dependency for foo", str(dist_dep))
        self.assertIn("Installed as dependency for foo", dist_dep.get_name_without_version())

    def test_local_distribution_shim_fallback(self):
        # Nonexistent path
        dist = pip_chill._LocalDistributionShim("/nonexistent/path")
        self.assertEqual(dist.metadata["Name"], "path")
        self.assertEqual(dist.version, "unknown")
        self.assertEqual(dist.requires, [])


if __name__ == "__main__":
    sys.exit(unittest.main())  # type: ignore
