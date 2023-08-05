# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os
import codecs


VERSION = (0, 1, 6)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

classes = """
    Development Status :: 5 - Production/Stable
    License :: OSI Approved :: BSD License
    Topic :: System :: Distributed Computing
    Topic :: Software Development :: Object Brokering
    Programming Language :: Python
    Programming Language :: Python :: 2
    Programming Language :: Python :: 2.6
    Programming Language :: Python :: 2.7
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.2
    Programming Language :: Python :: 3.3
    Programming Language :: Python :: Implementation :: CPython
    Programming Language :: Python :: Implementation :: PyPy
    Programming Language :: Python :: Implementation :: Jython
    Operating System :: OS Independent
    Operating System :: POSIX
    Operating System :: Microsoft :: Windows
    Operating System :: MacOS :: MacOS X
"""
classifiers = [s.strip() for s in classes.split('\n') if s]


if os.path.exists('README.md'):
    long_description = codecs.open('README.md', 'r', 'utf-8').read()
else:
    long_description = 'See https://github.com/SevenQuark/json-mapper'

setup(
    name='json-mapper',
    version=__versionstr__,
    description="Map and parse JSON text to python dict",
    long_description=long_description,
    author='SevenQuark',
    author_email='info@sevenquark.com',
    packages=find_packages(exclude=['ez_setup', 'tests', 'tests.*']),
    include_package_data=True,
    zip_safe=False,

    license='BSD',
    url='https://github.com/SevenQuark/json-mapper',

    classifiers=classifiers
)
