#!/usr/bin/env python
"""
Setup and install the opkg repo utils package.
"""

from distutils.core import setup

setup(
    name='opkg_repoutils',
    version='1.0.1',
    description='Tools for maintaining an opkg repository.',
    author='Kyle Isom',
    author_email='coder@kyleisom.net',
    license='ISC',
    url='http://bitbucket.org/kisom/opkg_repoutils',
    scripts=['scripts/opkg_repo_manager.py',],
    packages=['opkg_repo', ],
    requires=['yaml', 'pycrypto']
)
