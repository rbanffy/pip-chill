#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
]

test_requirements = [
    'pip'
]

setup(
    name='pip-chill',
    version='0.1.3',
    description="Like `pip freeze` but lists only the packages that are not "
    "dependencies of installed packages.",
    long_description=readme + '\n\n' + history,
    author="Ricardo Bánffy",
    author_email='rbanffy@gmail.com',
    url='https://github.com/rbanffy/pip-chill',
    packages=[
        'pip_chill',
    ],
    package_dir={'pip_chill':
                 'pip_chill'},
    entry_points={
        'console_scripts': [
            'pip-chill=pip_chill.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='pip-chill',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
