import sys

import pytest

from pip_chill import cli


class MockDistribution:
    def __str__(self):
        return "mockpkg==1.0.0"

    def get_name_without_version(self):
        return "mockpkg"


class MockDependency:
    def __str__(self):
        return "dep==0.1.0"

    def get_name_without_version(self):
        return "dep"


@pytest.fixture(autouse=True)
def fake_chill(monkeypatch):
    """Patch pip_chill.chill() to return mock data and record args."""
    calls = {}

    def fake_chill_func(*, show_all=False, no_chill=False):
        calls.update(show_all=show_all, no_chill=no_chill)
        return [MockDistribution()], [MockDependency()]

    monkeypatch.setattr(cli.pip_chill, "chill", fake_chill_func)
    return calls


@pytest.mark.parametrize(
    "argv,expected_flags",
    [
        ([], {"show_all": False, "no_chill": False}),
        (["--all"], {"show_all": True, "no_chill": False}),
        (["--no-chill"], {"show_all": False, "no_chill": True}),
        (["--all", "--no-chill"], {"show_all": True, "no_chill": True}),
    ],
)
def test_main_calls_chill_with_expected_flags(
    monkeypatch, fake_chill, argv, expected_flags, capsys
):
    monkeypatch.setattr(sys, "argv", ["pip-chill"] + argv)
    cli.main()
    captured = capsys.readouterr()
    # Output should show the mock distribution string
    assert "mockpkg==1.0.0" in captured.out
    assert fake_chill == expected_flags


def test_main_with_no_version(monkeypatch, fake_chill, capsys):
    monkeypatch.setattr(sys, "argv", ["pip-chill", "--no-version"])
    cli.main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "mockpkg"


def test_main_with_verbose(monkeypatch, fake_chill, capsys):
    monkeypatch.setattr(sys, "argv", ["pip-chill", "--verbose"])
    cli.main()
    captured = capsys.readouterr()
    lines = [line.strip() for line in captured.out.splitlines() if line.strip()]
    # Both distributions and dependencies printed
    assert "mockpkg==1.0.0" in lines
    assert "dep==0.1.0" in lines


def test_main_with_no_version_and_verbose(monkeypatch, fake_chill, capsys):
    monkeypatch.setattr(sys, "argv", ["pip-chill", "--no-version", "--verbose"])
    cli.main()
    captured = capsys.readouterr()
    lines = [line.strip() for line in captured.out.splitlines() if line.strip()]
    assert lines == ["mockpkg", "dep"]
