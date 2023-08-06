#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages, Command

# FIXME: Workaround faulty nose multiprocessing plugin
try:
    import multiprocessing
except ImportError:
    pass

class BuildDocs(Command):
    description = "Generates and updates the epydoc documentation"
    
    user_options = []
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass
    
    def run(self):
        import sys
        import subprocess
        
        subprocess.call("doc/build-docs.sh", stdout=sys.stdout, stderr=sys.stderr, shell=True)

# Read README file for the long description
here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README')).read()

# Read the version information
execfile(os.path.join(here, 'multivac', 'version.py'))

setup(
    name = 'multivac',
    version = __version__,
    packages = find_packages(),
    
    install_requires = [
        'Python >= 2.6',
        'SQLAlchemy < 0.7.999',
    ],
    test_suite = 'nose.collector',
    tests_require = [
        'nose',
        'nose-testconfig',
        'pysqlite',
    ],
    
    #description = "",
    long_description = README,
    author = 'Pau Tallada Crespí',
    author_email = 'pau.tallada@gmail.com',
    maintainer = 'Pau Tallada Crespí',
    maintainer_email = 'pau.tallada@gmail.com',
    url = "http://packages.python.org/multivac",
    
    license = 'AGPLv3+',
    #keywords = "",
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities"
    ],
    
    include_package_data=True,
    zip_safe=True,
    
    cmdclass = {'build_docs': BuildDocs},
)
