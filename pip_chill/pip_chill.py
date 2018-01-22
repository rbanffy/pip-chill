# -*- coding: utf-8 -*-
"""Lists installed packages that are not dependencies of others"""

import pip

from utils import Distribution


def chill(show_all=False):
    if show_all:
        ignored_packages = ()
    else:
        ignored_packages = {
            'pip', 'pip-chill', 'wheel', 'setuptools', 'pkg-resources'}

    # Gather all packages that are requirements and will be auto-installed.
    distributions = {}
    dependencies = {}

    for distribution in pip.get_installed_distributions():
        if distribution.key in ignored_packages:
            continue

        if distribution.key in dependencies:
            dependencies[distribution.key].version = distribution.version
        else:
            distributions[distribution.key] = \
                Distribution(distribution.key, distribution.version)

        for requirement in distribution.requires():
            if requirement.key not in ignored_packages:
                if requirement.key in dependencies:
                    dependencies[requirement.key] \
                        .required_by.add(distribution.key)
                else:
                    dependencies[requirement.key] = Distribution(
                        requirement.key,
                        required_by=(distribution.key,))

            if requirement.key in distributions:
                dependencies[requirement.key].version \
                    = distributions.pop(requirement.key).version

    return sorted(distributions.values()), sorted(dependencies.values())
