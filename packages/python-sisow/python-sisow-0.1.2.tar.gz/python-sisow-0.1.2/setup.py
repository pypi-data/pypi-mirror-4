"""\
"""
from distribute_setup import use_setuptools
use_setuptools()

import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

requires = ['lxml']

setup(
    name='python-sisow',
    version='0.1.2',
    description="Python programming interface to Sisow, Dutch iDeal Payment Service Provider",
    long_description=read('README.rst'),
    license="GPLv3",
    author="Robert-Reinder Nederhoed",
    author_email="r.r.nederhoed@gmail.com",
    url='https://github.com/nederhoed/python-sisow',
    keywords='ideal sisow finance',
    packages=find_packages(),
    test_suite="tests",
    install_requires=requires,
    classifiers = [
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ]
)
