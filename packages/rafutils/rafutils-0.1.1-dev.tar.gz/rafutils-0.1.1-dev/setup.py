#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup

with open('README.md') as file:
    long_description = file.read()

__version__ = '0.1.1-dev'

setup(
    name='rafutils',
    version=__version__,
    long_description=long_description,
    description='Utilities for Python development.',
    url='http://www.github.com/rfaulkner/rafutils',
    author="Ryan Faulkner",
    author_email="bobs.ur.uncle@gmail.com",
    packages=['rafutils',],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    data_files=[('readme', ['README.md'])]
)
