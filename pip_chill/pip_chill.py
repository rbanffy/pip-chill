"""Lists installed packages that are not dependencies of others"""

import re
import sys
import warnings
from functools import lru_cache
from importlib import metadata
from pathlib import Path
from typing import Dict, Generator, List, Set, Union

from packaging.requirements import InvalidRequirement, Requirement

STANDARD_PACKAGES = ("pip", "setuptools", "wheel")

RGX_PKG_NAME = r"([A-Za-z][\w.+\-]*)"  # base name (starts with a letter)
RGX_EXTRAS = r"(\[[^\]]+\])?"  # the extras contents including brackets
RGX_OPERATOR = r"(?:==|!=|>=|<=|~=|>|<)"
RGX_VERSION = rf"{RGX_OPERATOR}\s*[0-9]+(?:\.[0-9]+){{,2}}"
RGX_VERSION_LIST = rf"(?:\s*{RGX_VERSION}(?:\s*,\s*{RGX_VERSION})*)?"
RGX_MARKER = r"(?:\s*;\s*[A-Za-z0-9_\.\s<>=!~'\"(),\-]+)?"
RGX_COMMENTS = r"(?:\s*#.*)?"
RGX_REQ_LINE = rf"^{RGX_PKG_NAME}{RGX_EXTRAS}{RGX_VERSION_LIST}{RGX_MARKER}{RGX_COMMENTS}$"
PTN_REQ_LINE = re.compile(RGX_REQ_LINE, re.ASCII)


def _fallback_extract_name_extras(name: str) -> str:
    """
    Form a requirement string, extract with a regular expression the name and optional extras
    within the brackets
    """
    if not name.strip():
        warnings.warn(f"Invalid empty requirement string: {name!r}", stacklevel=2)
        return ""

    if match_package_and_extras := PTN_REQ_LINE.match(name):
        parts = match_package_and_extras.groups(default="")
        if extras := parts[1]:
            # remove brackets and split, then sort
            extras_list = [e.strip() for e in extras[1:-1].split(",")]
            extras_sorted = "[" + ",".join(sorted(extras_list)) + "]"
            parts = (parts[0], extras_sorted) + parts[2:]
        return "".join(parts)

    warnings.warn(f"Invalid requirement string: {name!r}", stacklevel=2)
    return name


def _extract_name_extras(name: str) -> str:
    """Form a requirement string, extract the name and optional extras within the brackets"""
    try:
        req = Requirement(name)
        extras = f"[{','.join(sorted(req.extras))}]" if req.extras else ""
        return f"{req.name}{extras}"
    except Exception:
        return _fallback_extract_name_extras(name)


def _normalize_name(dist: str) -> str:
    return dist.lower().replace("_", "-")


@lru_cache(maxsize=None)
def _find_egg_links() -> Generator[Path, None, None]:
    """Yield all .egg-link paths in non-standard locations."""
    return (
        egg_link
        for path_entry in sys.path
        if Path(path_entry).exists() and "site-packages" not in Path(path_entry).parts
        for egg_link in Path(path_entry).glob("*.egg-link")
    )


class Distribution:
    """
    Represents a distribution package installed in the current environment.
    """

    def __init__(self, name, version=None, required_by=None):
        self.name = name
        self.keyname = _normalize_name(name)
        self.version = version
        self.required_by = set(required_by) if required_by else set()

    @property
    def name_without_version(self):
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
        if isinstance(other, Distribution):
            return self.name == other.name
        return self.name == other

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return f"<{self.__module__}.{self.__class__.__name__} instance {self.name!r}>"

    def __str__(self):
        if self.required_by:
            return (
                f"# {self.name}=={self.version} # Installed as "
                f"dependency for {', '.join(sorted(self.required_by))}"
            )
        return f"{self.name}=={self.version}"


def _get_name_version_requires_from_location(location: Path):
    dist = metadata.PathDistribution(location)
    meta: metadata.PackageMetadata = dist.metadata
    name = meta["Name"] if "Name" in meta else location.name
    version = meta["Version"] if "Version" in meta else "unknown"
    dist_requires = dist.requires or []
    requires = []
    for req in dist_requires:
        if isinstance(req, Requirement):
            requires.append(req)
        else:
            try:
                requires.append(Requirement(req))
            except InvalidRequirement as e:
                warnings.warn(f"Skipping invalid requirement {req!r}: {e}", stacklevel=2)

    return name, version, requires


class _LocalDistributionShim:
    """A minimal stand-in for importlib.metadata.Distribution for legacy packages."""

    def _load_metadata(self):  # sourcery skip: extract-method
        """
        Attempts to load the distribution metadata from the path.
        """
        if not self._location.exists():
            return

        try:
            self.name, self._version, self._requires = _get_name_version_requires_from_location(
                self._location
            )
        except Exception:
            # fallback if metadata cannot be read
            self.name = self._location.name
            self._version = "unknown"
            self._requires = []

    def __init__(self, location: Union[str, Path]):
        self._location = Path(location)
        self.name = None
        self._version = None
        self._requires = None
        self._load_metadata()

    @property
    def metadata(self):
        return {"Name": self.name or self._location.name}

    @property
    def key(self) -> str:
        return _normalize_name(self.name or "")

    @property
    def version(self) -> str:
        return self._version or "unknown"

    @property
    def requires(self) -> List[Requirement]:
        return self._requires or []

    def __repr__(self) -> str:
        return f"<LocalDistShim {self.name or self._location} version={self.version}>"


def _iter_all_distributions() -> (
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
            if not dist.name:
                dist.name = egg_link.stem
        except OSError as e:
            warnings.warn(f"Skipping egg-link {egg_link}: {e}", stacklevel=2)
            continue
        except Exception as e:
            warnings.warn(f"Failed to read egg-link {egg_link}: {e}", stacklevel=2)
            continue
        if dist.key not in seen:
            seen.add(dist.key)
            yield dist


def _update_dist_and_deps(
    requirement,
    distribution_name: str,
    distribution_key: str,
    distributions: Dict[str, Distribution],
    dependencies: Dict[str, Distribution],
    ignored_packages: Set[str],
):
    """Process a single requirement and update distributions and dependencies in-place."""
    if isinstance(requirement, Requirement):
        requirement_name = requirement.name
        requirement_key = _normalize_name(requirement_name)
    else:
        try:
            requirement_name = requirement.split(";", 1)[0].strip()
            requirement_key = _normalize_name(_extract_name_extras(requirement_name))
        except Exception as e:
            warnings.warn(
                f"Skipping invalid requirement string {requirement!r} "
                f"from {distribution_name}: {e}",
                stacklevel=2,
            )
            return

    if requirement_key in ignored_packages or requirement_key in STANDARD_PACKAGES:
        return

    if requirement_key in dependencies:
        dependencies[requirement_key].required_by.add(distribution_key)
    else:
        dependencies[requirement_key] = Distribution(
            requirement_key, required_by={distribution_key}
        )

    if requirement_key in distributions:
        requirement = distributions.pop(requirement_key)
        dependencies[requirement_key].version = requirement.version


def chill(
    show_all: bool = False, no_chill: bool = False
) -> "tuple[List[Distribution], List[Distribution]]":

    ignored_packages = set() if show_all else {"pip", "wheel", "setuptools", "pkg-resources"}
    if no_chill:
        ignored_packages.add("pip-chill")

    distributions: Dict[str, Distribution] = {}
    dependencies: Dict[str, Distribution] = {}

    for distribution in _iter_all_distributions():
        try:
            distribution_name = distribution.name or distribution.metadata["Name"]
        except Exception as e:
            warnings.warn(f"Skipping distribution {distribution!r}: {e}", stacklevel=2)
            continue

        distribution_key = _normalize_name(distribution_name)
        if distribution_key in ignored_packages:
            continue

        requires = distribution.requires or []

        if distribution_key in dependencies:
            dependencies[distribution_key].version = distribution.version or "unknown"
        else:
            distributions[distribution_key] = Distribution(
                distribution_name, distribution.version or "unknown"
            )

        for requirement in requires:
            # Skip optional extras
            if isinstance(requirement, Requirement) and requirement.extras:
                continue
            # fallback: also skip strings with '; extra' if present
            if isinstance(requirement, str) and "; extra" in requirement:
                continue

            _update_dist_and_deps(
                requirement,
                distribution_name,
                distribution_key,
                distributions,
                dependencies,
                ignored_packages,
            )

    return sorted(distributions.values()), sorted(dependencies.values())
