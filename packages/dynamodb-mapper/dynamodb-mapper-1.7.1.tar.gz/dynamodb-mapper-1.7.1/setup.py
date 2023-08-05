#!/usr/bin/env python

import setuptools


setup_requires = [
    # d2to1 bootstrap
    'd2to1',

    # Testing dependencies (the application doesn't need them to *run*)
    'nose',
    'nosexcover',
    'coverage',
    'mock',
    'webtest'
]


setuptools.setup(
    setup_requires=setup_requires,
    d2to1=True,
    package_data={"dynamodb_mapper": [
    ]},
)
