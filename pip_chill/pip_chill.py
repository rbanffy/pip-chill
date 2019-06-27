# -*- coding: utf-8 -*-
"""Lists installed packages that are not dependencies of others"""

from pip._internal.operations.freeze import get_requirement_info
from pip._internal.utils.misc import get_installed_distributions


class Distribution:
    def __init__(self, name, version=None, required_by=None):
        self.name = name
        self.version = version
        self.required_by = set(required_by or [])

    def get_name_without_version(self):
        if self.required_by:
            return '# {} # Installed as dependency for {}' \
                .format(self.name, ', '.join(self.required_by))
        return self.name

    def __str__(self):
        if self.required_by:
            return '# {}=={} # Installed as dependency for {}' \
                .format(self.name, self.version, ', '.join(self.required_by))
        return '{}=={}'.format(self.name, self.version)

    def __eq__(self, other):
        if self is other:
            return True
        elif isinstance(other, Distribution):
            return self.name == other.name
        else:
            return self.name == other

    def __lt__(self, other):
        return self.name < other.name

    def __hash__(self):
        return hash(self.name)


def chill(show_all=False):
    if show_all:
        ignored_packages = set()
    else:
        ignored_packages = {'pip', 'wheel', 'setuptools', 'pkg-resources'}

    # Gather all packages that are requirements and will be auto-installed.
    distributions = {}  # mapping from package to version
    dependencies = {}  # mapping from package to its dependencies

    for distribution in get_installed_distributions():
        if distribution.key in ignored_packages:
            continue

        req, editable, _ = get_requirement_info(distribution)

        if editable:
            version = '{} -e {}'.format(distribution.version, req)
        else:
            version = distribution.version

        if distribution.key in dependencies:
            dependencies[distribution.key].version = version
        else:
            distributions[distribution.key] = \
                Distribution(distribution.key, version)

        for requirement in distribution.requires():
            if requirement.key not in ignored_packages:
                if requirement.key in dependencies:
                    dependencies[requirement.key] \
                        .required_by.add(distribution.key)
                else:
                    dependencies[requirement.key] = Distribution(
                        requirement.key,
                        required_by=(distribution.key,))

            # if the package is already in distributions, remove it
            # and move it into the dependencies
            if requirement.key in distributions:
                dependencies[requirement.key].version \
                    = distributions.pop(requirement.key).version

    return sorted(distributions.values()), sorted(dependencies.values())
