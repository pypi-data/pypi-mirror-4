# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os


VERSION = (0, 1, 2)
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


f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
long_description = f.read()
f.close()

setup(
    name='json-mapper',
    version=__versionstr__,
    description="Map and parse JSON text to python dict",
    long_description=long_description,
    author='SevenQuark',
    author_email='info@sevenquark.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    license='BSD',
    url='https://github.com/SevenQuark/json-mapper',

    classifiers=classifiers
)
