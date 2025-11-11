#!/bin/sh
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
