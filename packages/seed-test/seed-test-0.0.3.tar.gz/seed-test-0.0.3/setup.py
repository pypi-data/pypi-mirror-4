#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages
from dummy import __version__

setup(
    name="seed-test",
    version=__version__,
    author="Adam J. Gamble",
    author_email="mail@adamgamble.com",
    description=open('README').readline(),
    license='MIT',
    long_description='',
    packages=['dummy'],
    url="https://github.com/gamb/test-seed",
    include_package_data=True,
)
