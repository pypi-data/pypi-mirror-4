# -*- coding: utf-8 -*-
import setuptools

# this mixes setup deps with test deps, but our internal test tool
# (based on nosetests) was not working properly with test deps
setup_requires = [
    'd2to1',
    'nose',
    'nosexcover',
    'coverage',
    'mock',
    'webtest',
    'yanc',
]

setuptools.setup(
    setup_requires=setup_requires,
    d2to1=True,
    test_suite='nose.collector',
)
