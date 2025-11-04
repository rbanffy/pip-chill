# -*- coding: utf-8 -*-
"""Lists installed packages that are not dependencies of others"""

import sys
from importlib import metadata
from pathlib import Path
from re import split
from typing import Generator, Union

STANDARD_PACKAGES = ("pip", "setuptools", "wheel")


class Distribution:
    """
    Represents a distribution package installed in the current environment.
    """

    def __init__(self, name, version=None, required_by=None):
        self.name = name
        self.version = version
        self.required_by = set(required_by) if required_by else set()

    def get_name_without_version(self):
        """
        Return the name of the package without a version.
        """
        if self.required_by:
            return (
                f"# {self.name} # Installed as dependency for "
                f"{', '.join(sorted(self.required_by))}"
            )
        return self.name

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        if self is other:
            return True
        elif isinstance(other, Distribution):
            return self.name == other.name
        else:
            return self.name == other

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return f"<{self.__module__}.{self.__class__.__name__} instance '{self.name}'>"

    def __str__(self):
        if self.required_by:
            return (
                f"# {self.name}=={self.version} # Installed as "
                f"dependency for {', '.join(sorted(self.required_by))}"
            )
        return f"{self.name}=={self.version}"


class _LegacyDistributionShim:
    """A minimal stand-in for importlib.metadata.Distribution for legacy packages."""

    def __init__(self, name, location=None):
        self._name = name
        self._location = location

    @property
    def metadata(self):
        return {"Name": self._name}

    @property
    def version(self):
        return "unknown"

    @property
    def requires(self):
        return []

    def __repr__(self):
        return f"<LegacyDist {self._name} from {self._location}>"


def normalize_name(dist: str) -> str:
    return dist.lower().replace("_", "-")


def remove_version(name: str) -> str:
    sep = split(pattern=r"[^\w\-\.\[\]]", string=name, maxsplit=1)
    return sep[0]


def iter_all_distributions() -> (
    Generator[Union[metadata.Distribution, _LegacyDistributionShim], None, None]
):
    """
    Yield all installed distributions in the current environment, including editable installs,
    mimicking pkg_resources.working_set as closely as possible.

    Returns a generator of metadata.Distribution or _LegacyDistributionShim objects.
    """
    seen = set()  # track normalized package names

    # Yield standard distributions from importlib.metadata
    for dist in metadata.distributions():
        key = normalize_name(dist.metadata["Name"])
        if key not in seen:
            seen.add(key)
            yield dist

    # Yield editable installs (.egg-link)
    for path_entry in sys.path:
        path = Path(path_entry)
        if not path.exists():
            continue

        # .egg-link files (editable installs)
        for egg_link in path.glob("*.egg-link"):
            try:
                with egg_link.open() as f:
                    target = f.readline().strip()
                shim = _LegacyDistributionShim(target)
                key = normalize_name(shim.metadata["Name"])
            except Exception:
                continue

            if key not in seen:
                seen.add(key)
                yield shim

    # Ensure standard top-level packages exist
    # These are normally included by pip/virtualenv
    for pkg in STANDARD_PACKAGES:
        if pkg not in seen:
            try:
                dist = metadata.distribution(pkg)
                key = normalize_name(dist.metadata["Name"])
                if key not in seen:
                    seen.add(key)
                    yield dist
            except metadata.PackageNotFoundError:
                continue


def chill(
    show_all: bool = False, no_chill: bool = False
) -> "tuple[list[Distribution], list[Distribution]]":
    if show_all:
        ignored_packages = set()
    else:
        ignored_packages = {"pip", "wheel", "setuptools", "pkg-resources"}

    if no_chill:
        ignored_packages.add("pip-chill")

    distributions: dict[str, Distribution] = {}
    dependencies: dict[str, Distribution] = {}

    for distribution in iter_all_distributions():
        try:
            distribution_name = distribution.metadata["Name"]
        except Exception:
            continue

        distribution_key = normalize_name(distribution_name)
        # print("D distribution_key:", distribution_key)

        if distribution_key in ignored_packages:
            continue

        requires = getattr(distribution, "requires", None) or []

        if distribution_key in dependencies:
            dependencies[distribution_key].version = getattr(distribution, "version", "unknown")
        else:
            distributions[distribution_key] = Distribution(
                distribution_key,
                getattr(distribution, "version", "unknown"),
            )

        for requirement in requires:
            try:
                requirement_name = requirement.split(";", 1)[0].strip().split()[0]
                requirement_key = normalize_name(remove_version(requirement_name))
            except Exception:
                continue

            if requirement_key in ignored_packages:
                continue

            if requirement_key in STANDARD_PACKAGES:
                continue

            if requirement_key in dependencies:
                dependencies[requirement_key].required_by.add(distribution_key)
            else:
                dependencies[requirement_key] = Distribution(
                    requirement_key, required_by=(distribution_key,)
                )

            if requirement_key in distributions:
                dependencies[requirement_key].version = distributions.pop(requirement_key).version

    return sorted(distributions.values()), sorted(dependencies.values())
