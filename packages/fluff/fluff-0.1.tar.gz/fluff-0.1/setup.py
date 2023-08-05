#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="fluff",
    version="0.1",

    description="Extra tools for PyLint",
    url="https://github.com/dstufft/fluff/",

    packages=find_packages(exclude=["tests"]),

    zip_safe=False,
)
