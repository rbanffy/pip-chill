"""
Module allows for `python -m pip-chill`
Without this file, python -m pip_chill will work using the __main__.py,
but that does not align with the pip-chill name users expect
"""
from pip_chill import run

__name__ == '__main__' and run()
