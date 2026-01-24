"""Lists installed packages that are not dependencies of others"""

import re
from importlib import metadata

pattern = re.compile("[\s\(;=!<>]")


class Distribution:
    """
    Represents a distribution package installed in the current environment.
    """

    def __init__(
        self, name, version=None, required_by=None, hide_version=False
    ):
        self.name = name
        self.version = version
        self.required_by = set(required_by) if required_by else set()
        self.hide_version = hide_version

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
        return (
            f'<{self.__module__}.{self.__class__.__name__} instance "'
            f'{self.name}">'
        )

    def __str__(self):
        if self.required_by:
            if self.hide_version:
                return (
                    f"# {self.name} # Installed as "
                    f"dependency for {', '.join(sorted(self.required_by))}"
                )
            return (
                f"# {self.name}=={self.version} # Installed as "
                f"dependency for {', '.join(sorted(self.required_by))}"
            )
        if self.hide_version:
            return f"{self.name}"

        return f"{self.name}=={self.version}"


def chill(show_all=False, no_chill=False, no_version=False):
    """
    Returns a tuple of dicts, one with the the packages, other with their
    dependencies.
    """
    if show_all:
        ignored_packages = ()
    else:
        ignored_packages = {"pip", "wheel", "setuptools", "pkg-resources"}

    if no_chill:
        ignored_packages.add("pip-chill")

    # Gather all packages that are requirements and will be auto-installed.
    distributions = {}
    dependencies = {}

    for distribution in metadata.distributions():
        # importlib.metadata.distributions returns() an iterable of
        # importlib.metadata.PathDistribution objects. We'll be interested in
        # the name, version and requires attributes. The requires attribute is
        # a list of strings representing the requirement in requirements.txt
        # syntax. If the package has no requirements, the requires attribute
        # is None.

        # Skip packages to be ignored.
        if distribution.name in ignored_packages:
            continue

        # Populate the distributions dict.
        if distribution.name in dependencies:
            # If it is an already know dependency, we add the version.
            dependencies[distribution.name].version = distribution.version
        else:
            distributions[distribution.name] = Distribution(
                distribution.name,
                distribution.version,
                hide_version=no_version,
            )

        requirements = distribution.requires
        if requirements is not None:
            # Go over the requirements of this package and add any missing
            # dependencies.
            for requirement in requirements:
                # requirement is a string representing the requirement in
                # requirements.txt syntax. We'll need to parse it.
                requirement_name = re.split(pattern, requirement)[0]
                if requirement_name not in ignored_packages:
                    # We should not ignore this one
                    if requirement_name in dependencies:
                        # This is an already known dependency, we add the
                        # distribution to its required_by set.
                        dependencies[requirement_name].required_by.add(
                            distribution.name
                        )
                    else:
                        # This is a new dependency, we create a new
                        # Distribution object for it.
                        dependencies[requirement_name] = Distribution(
                            requirement_name,
                            required_by=(distribution.name,),
                            hide_version=no_version,
                        )

                # If the requirement is in the distributions list, remove it.
                # Add the distribution version to the dependency.
                if requirement_name in distributions:
                    dependencies[requirement_name].version = distributions.pop(
                        requirement_name
                    ).version

    return sorted(distributions.values()), sorted(dependencies.values())
