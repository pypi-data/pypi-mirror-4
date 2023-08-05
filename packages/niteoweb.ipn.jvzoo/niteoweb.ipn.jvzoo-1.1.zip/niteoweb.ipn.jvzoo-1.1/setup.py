# -*- coding: utf-8 -*-
"""Installer for the niteoweb.ipn.jvzoo package."""

from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = \
    read('README.rst') + \
    read('docs', 'CHANGELOG.rst') + \
    read('docs', 'LICENSE.rst')

setup(
    name='niteoweb.ipn.jvzoo',
    version='1.1',
    description="JVZoo IPN support in Plone.",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
    ],
    keywords='Plone IPN JVZoo',
    author='NiteoWeb Ltd.',
    author_email='info@niteoweb.com',
    url='http://pypi.python.org/pypi/niteoweb.ipn.jvzoo',
    license='BSD',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['niteoweb', 'niteoweb.ipn'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'five.grok',
        'niteoweb.ipn.core',
        'Plone',
        'plone.api',
        'setuptools',
    ],
    extras_require={
        'test': [
            'mock',
            'plone.app.testing',
            'unittest2',
        ],
        'develop': [
            'flake8',
            'jarn.mkrelease',
            'niteoweb.loginas',
            'plone.app.debugtoolbar',
            'plone.reload',
            'Products.Clouseau',
            'Products.DocFinderTab',
            'Products.PDBDebugMode',
            'Products.PrintingMailHost',
            'zest.releaser',
            'zptlint',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
