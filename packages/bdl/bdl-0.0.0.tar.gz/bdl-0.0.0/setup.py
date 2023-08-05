#!/usr/bin/env python
"""
bdl - bondage and discipline language
======

A collection of decorators (well, as of v0.0.0, just one) to make
Python a little more BDLish.  

"""

from setuptools import setup


setup(
    name='bdl',
    version='0.0.0',
    author='Adam DePrince',
    author_email='adeprince@nypublicradio.org',
    description='Bondage and Discipline, Python style.',
    long_description=__doc__,
    py_modules = [
        "bdl",
        ],
    packages = ["bdl"],
    zip_safe=True,
    license='Apache',
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development'
        ],
    url = "http://github.com/adamdeprince/bdl",
    install_requires = [
        ]
)

