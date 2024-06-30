#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "setuptools; python_version >= '3.12'",
]

test_requirements = ["pip"]

setup(
    name="pip-chill",
    version="1.0.2",
    description="Like `pip freeze` but lists only the packages that are not "
    "dependencies of installed packages.",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/x-rst",
    author="Ricardo Bánffy",
    author_email="rbanffy@gmail.com",
    url="https://github.com/rbanffy/pip-chill",
    packages=["pip_chill"],
    package_dir={"pip_chill": "pip_chill"},
    entry_points={"console_scripts": ["pip-chill=pip_chill.cli:main"]},
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords="pip-chill",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development",
    ],
    test_suite="tests",
    tests_require=test_requirements,
)
