#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages, Command

# FIXME: Workaround faulty nose ultiprocessing plugin
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

setup(
    name = 'multivac',
    version = '1.4.0',
    packages = find_packages(),
    
    install_requires = [
        'SQLAlchemy < 0.8',
    ],
    test_suite = 'nose.collector',
    tests_require = [
         'nose >= 0.11',
         'pysqlite'
    ],
    
    #description = "",
    #long_description = "",
    author = 'Pau Tallada Crespí',
    author_email = 'pau.tallada@gmail.com',
    maintainer = 'Pau Tallada Crespí',
    maintainer_email = 'pau.tallada@gmail.com',
    #url = '',
    
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
    
    cmdclass = {'build_docs': BuildDocs},
)
