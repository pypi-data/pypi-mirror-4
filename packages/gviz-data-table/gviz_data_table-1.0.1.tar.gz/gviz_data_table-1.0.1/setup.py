#!/usr/bin/python
#
# Copyright (C) 2012 - 2013 Charlie Clark

"""Python utility module Google Visualization Python API."""

__author__ = "Charlie Clark"

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import os
import sys

requires = ['setuptools']
if sys.version_info < (2, 7):
    requires.append('ordereddict')


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

extra = dict(
    docs=requires + ['sphinx', 'repoze.sphinx.autointerface']
    )

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst')) as f:
    CHANGES = f.read()

setup(
    name = "gviz_data_table",
    version = "1.0.1",
    description = "Python API for Google Visualization",
    long_description = README + '\n\n' +  CHANGES,
    author = __author__,
    author_email = 'charlie.clark@clark-consulting.eu',
    license = "BSD",
    keywords = 'charting graph Google Visualisation',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        ],
    url = "https://bitbucket.org/charlie_x/gviz-data-table",
    packages = find_packages(),
    install_requires = requires,
    tests_require = ['coverage', 'pytest', 'pytest-cov'],
    test_suite ='gviz_data_table',
    extras_require = extra,
    cmdclass = {'test': PyTest},
)
