##############################################################################
#
# Copyright Benji York and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Apache License, Version
# 2.0.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup for manuel package."""

from setuptools import setup, find_packages

long_description = (
    open('README.rst').read()
    + '\n\n'
    + open('CHANGES.txt').read()
    )

tests_require = ['zope.testing']

setup(
    name='manuel',
    version='1.7.2',
    url = 'http://pypi.python.org/pypi/manuel',
    packages=find_packages('src'),
    package_dir={'':'src'},
    zip_safe=False,
    author='Benji York',
    author_email='benji@benjiyork.com',
    description='Manuel lets you build tested documentation.',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        ],
    license='Apache Software License, Version 2.0',
    extras_require={
        'tests': tests_require,
        },
    tests_require = tests_require,
    test_suite = 'manuel.tests.test_suite',
    install_requires=[
        'setuptools',
        'six',
        ],
    include_package_data=True,
    long_description = long_description,
    )
