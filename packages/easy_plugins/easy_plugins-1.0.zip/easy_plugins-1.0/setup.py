#!/usr/bin/env python

from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys

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

setup(name='easy_plugins',
    version='1.0',
    description='Keep your plugins simple, stupid!',
    author='Stanislav Prokop',
    author_email='prost87@gmail.com',
    url='https://bitbucket.org/prost87/easyplugins',
    packages=['easy_plugins'],
    license='LICENSE.txt',
    long_description=open('README.txt').read(),
    tests_require=['pytest'],
    cmdclass = {'test': PyTest},
)