#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import click

import pip_chill


@click.command()
@click.option(
    '--no-version', is_flag=True, default=False, help='Omit version numbers.')
@click.option(
    'show_all', '--all', is_flag=True, default=False,
    help='Show all packages.')
@click.option(
    '--verbose', '-v', is_flag=True, default=False,
    help='List commented out dependencies too'
)
def main(no_version=False, show_all=False, verbose=False):
    """Console script for pip_chill"""
    distributions, dependencies = pip_chill.chill(show_all=show_all)
    for package in distributions:
        if no_version:
            print(package.get_name_without_version())
        else:
            print(package)

    if verbose:
        for package in dependencies:
            if no_version:
                print(package.get_name_without_version())
            else:
                print(package)


if __name__ == "__main__":
    main()
