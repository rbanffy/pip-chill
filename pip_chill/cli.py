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
def main(no_version, show_all):
    """Console script for pip_chill"""
    for package, version in pip_chill.chill(show_all=show_all):
        if no_version:
            print(package)
        else:
            print('{}=={}'.format(package, version))

if __name__ == "__main__":
    main()
