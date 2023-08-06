#!/usr/bin/env python
import os
import sys
from setuptools import setup, find_packages

sys.path.insert(0, './src')
from kforge import __version__

setup(
    name='kforge',
    version=__version__,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    scripts = [ 
        os.path.join('bin', 'kforge-admin'),
        os.path.join('bin', 'kforge-makeconfig'),
        os.path.join('bin', 'kforge-ssh-handler'),
        os.path.join('bin', 'kforge-test'),
        os.path.join('bin', 'kforgevirtualenvhandlers.py'),
    ],
    include_package_data = True,
    zip_safe = False,
    install_requires = [
        'domainmodel==0.15',
        'Routes>=1.7.2,<=1.10.3',
        'rawdog',
    ],
    author='Appropriate Software Foundation and Open Knowledge Foundation',
    author_email='john.bywater@appropriatesoftware.net',
    license='AGPL',
    url='http://www.kforgeproject.com/',
    description='Enterprise architecture for project hosting',
    long_description = open('README').read(),
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
