# -*- coding: utf-8 -*-
"""Installer for this package."""

from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = \
    read('README.rst') + \
    read('docs', 'HISTORY.rst') + \
    read('docs', 'LICENSE.rst')

setup(
    name='chimprewriter',
    version="0.1",
    description="Python bindings for ChimpRewriter API",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
    ],
    keywords='API spinner ChimpRewriter',
    author='NiteoWeb Ltd.',
    author_email='info@niteoweb.com',
    url='http://www.niteoweb.com',
    license='BSD',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
    ],
    extras_require={
        # list libs needed for unittesting this project
        'test': [
            'mock',
            'unittest2',
        ],
        # list libs needed for releasing this project
        'release': [
            'zest.releaser',   # bin/longtest
            'jarn.mkrelease',  # bin/mkrelease
        ],
    },
)
