# -*- coding: utf-8 -*-
import setuptools

# Distribute *must* be installed (create your virtualenv with --distribute).
if not hasattr(setuptools, "_distribute"):
    raise SystemExit(
        """Setuptools is not supported.
        Please install Distribute (create your virtualenv with --distribute)"""
    )

setup_requires = [
    'd2to1',
    'nose',
    'nosexcover',
    'coverage',
    'mock',
    'webtest',
    ]

setuptools.setup(
    setup_requires=setup_requires,
    d2to1=True,
    test_suite = "nose.collector",
    package_data={'pyramid_facebook': [
        ]},
    paster_plugins=['pyramid'],
    )
