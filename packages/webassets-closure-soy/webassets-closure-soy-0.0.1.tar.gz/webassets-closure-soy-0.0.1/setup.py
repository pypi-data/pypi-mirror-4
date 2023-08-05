#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name="webassets-closure-soy",
        version="0.0.1",
        description="Integration of Google's Soy Template Compiler with the webassets package.",
        long_description=open("README.rst").read(),
        author="Michael Su",
        author_email="mdasu1@gmail.com",
        url="https://pypi.python.org/pypi/webassets-closure-soy/",
        packages=find_packages(),
        install_requires=['webassets'],
        )
