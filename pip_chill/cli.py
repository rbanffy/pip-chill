#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import click
import pip_chill


@click.option(
    '--no-version', is_flag=True, default=False, help='Omit version numbers.')
@click.command()
def main(no_version):
    """Console script for pip_chill"""
    for package, version in pip_chill.chill():
        if no_version:
            print(package)
        else:
            print('{}=={}'.format(package, version))

if __name__ == "__main__":
    main()
