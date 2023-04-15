# -*- coding: utf-8 -*-
"""Lists installed packages that are not dependencies of others"""

import pkg_resources


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
        return (
            f'<{self.__module__}.{self.__class__.__name__} instance "'
            f'{self.name}">'
        )

    def __str__(self):
        if self.required_by:
            return (
                f"# {self.name}=={self.version} # Installed as "
                f"dependency for {', '.join(sorted(self.required_by))}"
            )
        return f"{self.name}=={self.version}"


def chill(show_all=False, no_chill=False):
    if show_all:
        ignored_packages = ()
    else:
        ignored_packages = {"pip", "wheel", "setuptools", "pkg-resources"}

    if no_chill:
        ignored_packages.add("pip-chill")

    # Gather all packages that are requirements and will be auto-installed.
    distributions = {}
    dependencies = {}

    for distribution in pkg_resources.working_set:
        if distribution.key in ignored_packages:
            continue

        if distribution.key in dependencies:
            dependencies[distribution.key].version = distribution.version
        else:
            distributions[distribution.key] = Distribution(
                distribution.key, distribution.version
            )

        for requirement in distribution.requires():
            if requirement.key not in ignored_packages:
                if requirement.key in dependencies:
                    dependencies[requirement.key].required_by.add(
                        distribution.key
                    )
                else:
                    dependencies[requirement.key] = Distribution(
                        requirement.key, required_by=(distribution.key,)
                    )

            if requirement.key in distributions:
                dependencies[requirement.key].version = distributions.pop(
                    requirement.key
                ).version

    return sorted(distributions.values()), sorted(dependencies.values())
