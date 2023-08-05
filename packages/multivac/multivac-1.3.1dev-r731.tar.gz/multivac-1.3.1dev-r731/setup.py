#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name = 'multivac',
    version = '1.3.1',
    packages = find_packages(),
    
    install_requires = [
        'SQLAlchemy < 0.8',
    ],
    test_suite = 'multivac.test',
    tests_require = [
         'nose >= 0.11'
    ],
    
    #description = "",
    #long_description = "",
    author = 'Pau Tallada Crespí',
    author_email = 'pau.tallada@gmail.com',
    maintainer = 'Pau Tallada Crespí',
    maintainer_email = 'pau.tallada@gmail.com',
    #url = '',
    
    license = 'GPLv3+',
    #keywords = "",
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities"
    ],
)
