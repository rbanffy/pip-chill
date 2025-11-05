# -*- coding: utf-8 -*-
"""Lists installed packages that are not dependencies of others"""
import re
import sys
import warnings
from functools import lru_cache
from importlib import metadata
from pathlib import Path
from typing import Dict, Generator, List, Union

from packaging.requirements import Requirement

STANDARD_PACKAGES = ("pip", "setuptools", "wheel")


def _normalize_name(dist: str) -> str:
    return dist.lower().replace("_", "-")


rgx_pkg_name = r"([A-Za-z][\w.+\-]*)"  # base name (starts with a letter)
rgx_extras = r"(\[[^\]]+\])?"  # the extras contents including brackets
rgx_operator = r"(?:==|!=|>=|<=|~=|>|<)"
rgx_version = rf"{rgx_operator}\s*[0-9]+(?:\.[0-9]+){{,2}}"
rgx_version_list = rf"(?:\s*{rgx_version}(?:\s*,\s*{rgx_version})*)?"
rgx_marker = r"(?:\s*;\s*[A-Za-z0-9_\.\s<>=!~'\"(),\-]+)?"
rgx_comments = r"(?:\s*#.*)?"
rgx_req_line = rf"^{rgx_pkg_name}{rgx_extras}{rgx_version_list}{rgx_marker}{rgx_comments}$"
ptn_req_line = re.compile(rgx_req_line, re.ASCII)


def fallback_extract_name_extras(name: str) -> str:
    if not name.strip():
        warnings.warn(f"Invalid empty requirement string: {name!r}")
        return ""

    # Match <package>[extras] ignoring version specifiers
    match = ptn_req_line.match(name)
    if match:
        parts = match.groups(default="")
        extras = parts[1]
        if extras:
            # remove brackets and split, then sort
            extras_list = [e.strip() for e in extras[1:-1].split(",")]
            extras_sorted = "[" + ",".join(sorted(extras_list)) + "]"
            parts = (parts[0], extras_sorted) + parts[2:]
        return "".join(parts)

        return "".join(match.groups(default=""))

    warnings.warn(f"Invalid requirement string: {name!r}")
    return name


def extract_name_extras(name: str) -> str:
    try:
        req = Requirement(name)
        extras = f"[{','.join(sorted(req.extras))}]" if req.extras else ""
        return f"{req.name}{extras}"
    except Exception:
        return fallback_extract_name_extras(name)


@lru_cache(maxsize=None)
def _find_egg_links() -> List[Path]:
    """Return all .egg-link paths in non-standard locations."""
    egg_links = []
    for path_entry in sys.path:
        path = Path(path_entry)
        if not path.exists() or "site-packages" in str(path):
            continue
        egg_links.extend(path.glob("*.egg-link"))
    return egg_links


class Distribution:
    """
    Represents a distribution package installed in the current environment.
    """

    def __init__(self, name, version=None, required_by=None):
        self.name = name
        self.keyname = _normalize_name(name)
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


class _LocalDistributionShim:
    """A minimal stand-in for importlib.metadata.Distribution for legacy packages."""

    def __init__(self, location: Union[str, Path]):
        self._location = Path(location)
        self._name = None
        self._version = None
        self._requires = None
        self._load_metadata()

    def _load_metadata(self):
        """
        Attempts to load the distribution metadata from the path.
        """
        if not self._location.exists():
            return

        try:
            dist = metadata.PathDistribution(self._location)
            self._name = dist.metadata.get("Name", self._location.name)
            self._version = dist.metadata.get("Version", "unknown")
            requires = dist.requires or []
            self._requires = [
                req if isinstance(req, Requirement) else Requirement(req) for req in requires
            ]
        except Exception:
            # fallback if metadata cannot be read
            self._name = self._location.name
            self._version = "unknown"
            self._requires = []

    @property
    def metadata(self):
        return {"Name": self._name or self._location.name}

    @property
    def key(self) -> str:
        return _normalize_name(self._name or "")

    @property
    def version(self) -> str:
        return self._version or "unknown"

    @property
    def requires(self) -> List[Requirement]:
        return self._requires or []

    def __repr__(self) -> str:
        return f"<LocalDistShim {self._name or self._location} version={self.version}>"


def iter_all_distributions() -> (
    Generator[Union[metadata.Distribution, _LocalDistributionShim], None, None]
):
    """
    Yield all installed distributions in the current environment, including editable installs,
    mimicking pkg_resources.working_set as closely as possible.

    Returns a generator of metadata.Distribution or _LocalDistributionShim objects.
    """
    seen = set()  # track normalized package names

    # Ensure standard top-level packages exist
    # These are normally included by pip/virtualenv
    for pkg in STANDARD_PACKAGES:
        try:
            dist = metadata.distribution(pkg)
            package_name = _normalize_name(dist.metadata["Name"])
            if package_name not in seen:
                seen.add(package_name)
                yield dist
        except metadata.PackageNotFoundError:
            continue

    # Yield standard distributions from importlib.metadata
    for dist in metadata.distributions():
        package_name = _normalize_name(dist.metadata["Name"])
        if package_name not in seen:
            seen.add(package_name)
            yield dist

    # Yield editable installs (.egg-link) / non-standard paths
    for egg_link in _find_egg_links():
        try:
            target_path = egg_link.read_text().splitlines()[0].strip()
            dist = _LocalDistributionShim(target_path)
            if not dist._name:
                dist._name = egg_link.stem
        except Exception:
            continue

        if dist.key not in seen:
            seen.add(dist.key)
            yield dist


def chill(
    show_all: bool = False, no_chill: bool = False
) -> "tuple[List[Distribution], List[Distribution]]":

    ignored_packages = set() if show_all else {"pip", "wheel", "setuptools", "pkg-resources"}

    if no_chill:
        ignored_packages.add("pip-chill")

    distributions: Dict[str, Distribution] = {}
    dependencies: Dict[str, Distribution] = {}

    for distribution in iter_all_distributions():
        try:
            distribution_name = getattr(distribution, "name", distribution.metadata["Name"])
        except Exception:
            continue

        distribution_key = _normalize_name(distribution_name)
        if distribution_key in ignored_packages:
            continue

        requires = getattr(distribution, "requires", None) or []

        if distribution_key in dependencies:
            dependencies[distribution_key].version = getattr(distribution, "version", "unknown")
        else:
            distributions[distribution_key] = Distribution(
                distribution_name,
                getattr(distribution, "version", "unknown"),
            )

        for requirement in requires:
            if isinstance(requirement, Requirement):
                requirement_name = requirement.name
                requirement_key = _normalize_name(requirement_name)
            else:
                try:
                    requirement_name = requirement.split(";", 1)[0].strip()
                    requirement_key = _normalize_name(extract_name_extras(requirement_name))
                except Exception:
                    continue

            if requirement_key in ignored_packages or requirement_key in STANDARD_PACKAGES:
                continue

            if requirement_key in dependencies:
                dependencies[requirement_key].required_by.add(distribution_key)
            else:
                dependencies[requirement_key] = Distribution(
                    requirement_key, required_by={distribution_key}
                )

            if requirement_key in distributions:
                dependencies[requirement_key].version = distributions.pop(requirement_key).version

    return sorted(distributions.values()), sorted(dependencies.values())
