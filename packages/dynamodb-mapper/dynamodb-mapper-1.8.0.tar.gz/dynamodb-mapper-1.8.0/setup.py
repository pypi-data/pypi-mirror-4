#!/usr/bin/env python

import setuptools

setup_requires = [
    'd2to1',
    'nose',
    'nosexcover',
    'coverage',
    'mock',
]

setuptools.setup(
    setup_requires=setup_requires,
    d2to1=True,
    test_suite="nose.collector",
    package_data={"dynamodb_mapper": []},
)
