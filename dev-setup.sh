#!/bin/sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements_dev.txt
python setup.py develop
