import re
import subprocess  # nosec B404
import warnings

import pytest

from pip_chill.pip_chill import (  # noqa: I101
    RGX_EXTRAS,
    RGX_OPERATOR,
    RGX_REQ_LINE,
    RGX_VERSION,
    RGX_VERSION_LIST,
    Distribution,
    LocalDistributionShim,
    chill,
    extract_name_extras,
    fallback_extract_name_extras,
    get_name_version_requires_from_location,
    update_dist_and_deps,
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
    ("", "", True),
    (" ; python_version<'3.10'", " ; python_version<'3.10'", True),
]


@pytest.fixture
def distributions():
    d1 = Distribution("pip-chill", "2.0.0", [])
    d2 = Distribution("pip", "10.0.0", [d1])
    d3 = Distribution("pip", "11.0.0", [d1])
    return d1, d2, d3


def test_distribution_str_with_dependencies():
    dist = Distribution("foo", "1.0.0", required_by={"bar", "baz"})
    s = str(dist)
    assert "Installed as dependency for" in s
    assert "foo==1.0.0" in s


def test_pip_omitted():
    packages, _ = chill()
    names = {p.name for p in packages}
    assert all(pkg not in names for pkg in ["pip", "setuptools", "wheel"])


def test_show_all_includes_expected():
    packages, _ = chill(show_all=True)
    names = {p.name for p in packages}
    assert {"pip", "pip-chill"} <= names


def test_distribution_hash():
    packages, _ = chill()
    assert all(hash(p) == hash(p.name) for p in packages)


def test_distribution_equality(distributions):
    d1, d2, d3 = distributions
    assert d1 != d2
    assert d1 == d1
    assert d2 == d3
    assert d2 == d2.name


@pytest.mark.parametrize(
    "args,expected_code",
    [
        ("--help", 0),
        ("--no-version", 0),
        ("--verbose", 0),
        ("-v", 0),
        ("--verbose --no-version", 0),
        ("--invalid-option", 2),
    ],
)
def test_cli_invocations(args, expected_code):
    cli_args = args.split()
    cmd = ["python", "pip_chill/cli.py"] + cli_args
    result = subprocess.run(cmd, capture_output=True, text=True)  # nosec B404,B603
    assert result.returncode == expected_code

    assert (
        ("--no-version" in result.stdout and "omit version numbers" in result.stdout)
        if "--help" in cli_args
        else True
    )
    assert (
        ("==" not in result.stdout and ">=" not in result.stdout)
        if "--no-version" in cli_args
        else True
    )
    assert (
        "# Installed as dependency for" in result.stdout
        if any(f in cli_args for f in ["--verbose", "-v"])
        else True
    )


@pytest.mark.parametrize("flag", ["--all", "-a", "--show-all"])
def test_cli_all_flags(flag):
    result = subprocess.run(
        ["python", "pip_chill/cli.py", flag],
        capture_output=True,
        text=True,
    )  # nosec B404, B603, B607
    assert result.returncode == 0
    assert all(pkg in result.stdout for pkg in ["pip", "pip-chill"])


def test_cli_no_chill():
    result = subprocess.run(
        ["python", "pip_chill/cli.py", "--no-chill"], capture_output=True, text=True
    )  # nosec B404, B603, B607
    assert result.returncode == 0
    assert "pip-chill" not in result.stdout


def test_regex_patterns_match():
    assert all(
        re.match(pat, val)
        for pat, val in [
            (RGX_OPERATOR, "=="),
            (RGX_OPERATOR, ">"),
            (RGX_VERSION, ">2"),
            (RGX_VERSION_LIST, ">=2.3.4, <4"),
            (RGX_EXTRAS, "[>=2.3.4]"),
            (RGX_REQ_LINE, "requests[extra1, extra2]>=2"),
        ]
    )
    assert not re.match(RGX_REQ_LINE, "invalid package string")


def test_distribution_str_and_name_without_version():
    dist_top = Distribution("foo", "1.2.3")
    dist_dep = Distribution("bar", "2.0", required_by={"foo"})
    assert str(dist_top) == "foo==1.2.3"
    assert dist_top.get_name_without_version() == "foo"
    assert "bar" in str(dist_dep)
    assert "Installed as dependency for foo" in str(dist_dep)
    assert "Installed as dependency for foo" in dist_dep.get_name_without_version()


def test_chill_skips_distribution_with_exception(monkeypatch):
    class BadDist:
        @property
        def name(self):
            raise ValueError("bad")

        @property
        def metadata(self):
            return {"Name": "ignored"}

        @property
        def requires(self):
            return []

    monkeypatch.setattr("pip_chill.pip_chill.iter_all_distributions", lambda: [BadDist()])
    import warnings

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        dists, deps = __import__("pip_chill.pip_chill").pip_chill.chill()
    assert dists == []
    assert any("Skipping distribution" in str(wi.message) for wi in w)


def test_update_dist_and_deps_moves_distribution():
    dist = Distribution("pkg", "1.2.3")
    distributions = {"pkg": dist}
    dependencies = {"other": Distribution("other")}
    update_dist_and_deps("pkg", "foo", "foo", distributions, dependencies, set())
    assert "pkg" not in distributions
    assert dependencies["pkg"].version == "1.2.3"
    assert "foo" in dependencies["pkg"].required_by


def test_local_distribution_shim_defaults():
    legacy = LocalDistributionShim("legacy-pkg")
    assert legacy.metadata["Name"] == "legacy-pkg"
    assert legacy.version == "unknown"
    assert legacy.requires == []
    assert "legacy-pkg" in str(legacy)


def test_local_distribution_shim_fallback():
    dist = LocalDistributionShim("/nonexistent/path")
    assert dist.metadata["Name"] == "path"
    assert dist.version == "unknown"
    assert dist.requires == []


def test_local_distribution_shim_load_metadata_fallback(tmp_path):
    shim = LocalDistributionShim(tmp_path / "no_such_file")
    assert shim.version == "unknown"
    assert shim.requires == []
    assert shim.metadata["Name"] == "no_such_file"


@pytest.mark.parametrize("func", [extract_name_extras, fallback_extract_name_extras])
@pytest.mark.parametrize("req,expected,should_warn", TEST_REQUIREMENTS)
def test_extract_name_extras_variants(func, req, expected, should_warn):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = func(req)
    got_warn = any("Invalid" in str(wr.message) for wr in w)
    assert result == expected
    assert got_warn == should_warn


@pytest.mark.parametrize("req", ["", " ; python_version<'3.10'", "invalid package string"])
def test_fallback_extract_name_extras_warns(req):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = fallback_extract_name_extras(req)
    assert isinstance(result, str)
    assert any("Invalid" in str(wi.message) for wi in w)


def test_get_name_version_requires_from_location_invalid(tmp_path):
    dummy_file = tmp_path / "dummy.dist-info"
    dummy_file.write_text("not a valid metadata")
    name, version, requires = get_name_version_requires_from_location(dummy_file)
    assert isinstance(name, str)
    assert isinstance(version, str)
    assert isinstance(requires, list)


def test_update_dist_and_deps_invalid_requirement():
    distributions = {}
    dependencies = {}
    with warnings.catch_warnings(record=True) as warn:
        warnings.simplefilter("always")
        update_dist_and_deps("pkg ???", "dist", "dist", distributions, dependencies, set())
    assert any("Skipping invalid requirement" in str(warn_i.message) for warn_i in warn) or any(
        "Invalid requirement string" in str(warn_i.message) for warn_i in warn
    )


def test_chill_handles_missing_name(monkeypatch):
    class DummyDist:
        name = None
        version = "1.0"
        requires = []

        @property
        def metadata(self):
            return {"Name": "dummy"}

    monkeypatch.setattr("pip_chill.pip_chill.iter_all_distributions", lambda: [DummyDist()])
    distributions, deps = chill()
    assert any(d.name == "dummy" for d in distributions)
