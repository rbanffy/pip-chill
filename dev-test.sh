#!/bin/sh
flake8 pip_chill tests
pytest
tox
