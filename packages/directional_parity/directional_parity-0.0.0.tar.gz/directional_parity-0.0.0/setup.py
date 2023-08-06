#!/usr/bin/env python
"""
directional_parity
======


"""

from setuptools import setup


setup(
    name='directional_parity',
    version='0.0.0',
    author='Adam DePrince',
    author_email='adeprince@nypublicradio.org',
    description='Direction detecting parity - developed for project.wnyc.org/cicadas',
    long_description=__doc__,
    py_modules = [
        'directional_parity/__init__',
        'directional_parity/encoder',
        'directional_parity/decoder',
        'directional_parity/temperature',
        ],
    packages = ["directional_parity"],
    zip_safe=True,
    include_package_data=True,
    classifiers=[
        ],
    scripts = [
        'scripts/directional_parity_encode',
        'scripts/directional_parity_decode',
        'scripts/wnyc_cicada_decode_temp',
        ],
    url = "https://github.com/adamdeprince/wnyc_systems",
    install_requires = [
        ]
)

