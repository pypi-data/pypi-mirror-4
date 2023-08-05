#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name          = 'HPPPM',
    version       = '0.1',
    description   = 'Webservices API for HP Project and Portfolio Management',
    author        = 'Varun Juyal',
    author_email  = 'varunjuyal123@yahoo.com',
    url           = 'http://pypi.python.org/pypi/HPPPM-Management/0.1',
    license       = 'PSF',
    packages      = find_packages(),
    scripts       = ['hpppm/bin/hpppm_demand_management.py'],
    install_requires = ['lxml', 'jinja2', 'httplib >=1.1', 'mechanize >=0.2.5'],
    include_package_data = True,
)


