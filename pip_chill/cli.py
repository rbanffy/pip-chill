#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import click
import pip_chill


@click.command()
def main(args=None):
    """Console script for pip_chill"""
    for line in pip_chill.chill():
        print(line)

if __name__ == "__main__":
    main()
