#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse

import pip_chill


def main():
    """Console script for pip_chill"""

    parser = argparse.ArgumentParser(
        description="Like `pip freeze`, but more relaxed."
    )
    parser.add_argument(
        "--no-version",
        action="store_true",
        dest="no_version",
        help="omit version numbers.",
    )
    parser.add_argument(
        "-a",
        "--all",
        "--show-all",
        action="store_true",
        dest="show_all",
        help="show all packages.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        help="list commented out dependencies too.",
    )
    parser.add_argument(
        "-o",
        "--omit-self",
        action="store_true",
        dest="omit_self",
        help="dont display pip-chill itself",
    )
    args = parser.parse_args()

    distributions, dependencies = pip_chill.chill(show_all=args.show_all, omit_self=args.omit_self)
    for package in distributions:
        if args.no_version:
            print(package.get_name_without_version())
        else:
            print(package)

    if args.verbose:
        for package in dependencies:
            if args.no_version:
                print(package.get_name_without_version())
            else:
                print(package)


if __name__ == "__main__":
    main()
