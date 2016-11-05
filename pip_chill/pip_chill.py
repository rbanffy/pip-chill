# -*- coding: utf-8 -*-
"""Lists installed packages that are not dependencies of others"""

import pip


def chill(show_all=False):

    if show_all:
        ignored_packages = ()
    else:
        ignored_packages = ('pip', 'pip-chill', 'wheel', 'setuptools')

    # Gather all packages that are requirements and will be auto-installed.
    dependencies = set()
    for distribution in pip.get_installed_distributions():
        for requirement in distribution.requires():
            dependencies.add(requirement.key)

    # List all packages and versions installed, excluding the auto-installed.
    return [
        (distribution.key, distribution.version)
        for distribution in pip.get_installed_distributions()
        if distribution.key not in dependencies
        and distribution.key not in ignored_packages
    ]
