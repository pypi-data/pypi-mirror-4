#!/usr/bin/env python

from distutils.core import setup

setup (name = "ImmutablePy",
       version = "0.1",
       description = "Support for working with immutable data",
       long_description = 
"""This package provides support for working with immutable data. There is a base class for defining immutable instances. Once initialized, the attributes of such instances are frozen. There are also fully immutable versions of lists/tuples, dictionaries, and sets. Immutability is imposed in a stricter sense than for Python's tuples or frozensets: to qualify as immutable, all of an object's elements and attributes must be immutable as well.""",
       author = "Konrad Hinsen",
       author_email = "konrad.hinsen@cnrs-orleans.fr",
       license = "CeCILL-B",
       url = "http://bitbucket.org/khinsen/immutablepy",
       packages = ['immutable'],
       )
