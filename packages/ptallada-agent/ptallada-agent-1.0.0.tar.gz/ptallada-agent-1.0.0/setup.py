# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()

setup(
    name = "ptallada-agent",
    version = '1.0.0',
    packages = find_packages(),
    
    install_requires = [
        'python-daemon<1.6',
        'lockfile<0.9',
    ],
    test_suite = 'nose.collector',
    tests_require = [
         'nose >= 0.11',
         'pysqlite'
    ],
    
    description = ("A wrapper around python-daemon to change pidfile handling."),
    long_description = README,
    author = 'Pau Tallada Crespí',
    author_email = 'pau.tallada@gmail.com',
    maintainer = 'Pau Tallada Crespí',
    maintainer_email = 'pau.tallada@gmail.com',
    url = "http://packages.python.org/python-agent",
    
    license = 'AGPLv3+',
    keywords = "daemon agent singleton pid background",
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities"
    ],
    
    include_package_data=True,
    zip_safe=True,
)