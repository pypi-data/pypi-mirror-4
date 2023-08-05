#!/usr/bin/env python
"""Chroniker
======

Performance monitoring tools in Python

"""

from setuptools import setup

setup(
    name="chroniker",
    version='0.0.0',
    author='Adam DePrince',
    author_email='adeprince@nypublicradio.org',
    description='Profiling and timing tools for Python.',
    py_modules = ['chroniker'],
    packages = ['chroniker'],
    zip_safe=True,
    license='BSD',
    include_package_data = True,
    classifiers = [
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'],
    url = 'http://github.com/wnyc/to_sentry'
)
       
