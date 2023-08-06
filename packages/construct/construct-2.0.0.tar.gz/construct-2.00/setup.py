#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="construct",
    version="2.00",
    description=("library for constructing (parsing and building) of binary "
                "and textual data structures"),
    author="Tomer Filiba",
    author_email="tomerfiliba at gmail dot com",
    url="http://construct.wikispaces.com/",
    platforms = ["any"],
    long_description="""
Construct is a library for parsing and building of data structures (binary or
textual).

It is based on the concept of defining data structures in a declarative manner,
rather than procedural code: more complex constructs are composed of a hierarchy
of simpler ones. It's the first library that makes parsing fun, instead of the
usual headache it is today.

Construct features bit and byte granularity, symmetrical operation (parsing
and building), component-oriented design (declarative), easy debugging and
testing, easy to extend (subclass constructs), and lots of primitive constructs
to make your work easier (fields, structs, unions, repeaters, meta constructs,
switches, on-demand parsing, pointers, etc.)""",
    packages=find_packages(),
    package_data={'': ['*.*']},
    keywords="parsing, binary, bitwise, bit level, constructing, struct",
    classifiers=[
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "License :: Public Domain",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Topic :: Internet",
    "Topic :: Scientific/Engineering :: Information Analysis",
    "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Networking",
    "Topic :: System :: Networking :: Monitoring",
    "Topic :: Text Processing",
    ],
)
