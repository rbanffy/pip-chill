#!/bin/sh
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,test,docs]"
pre-commit install
