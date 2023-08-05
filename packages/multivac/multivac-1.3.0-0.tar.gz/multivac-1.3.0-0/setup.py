#!/usr/bin/env python

from setuptools import setup, find_packages
requires = [
        'SQLAlchemy<0.8',
        ]
setup(
    name='multivac',
    version='1.3.0-0',
    packages=find_packages(),
    install_requires=requires,)
    
