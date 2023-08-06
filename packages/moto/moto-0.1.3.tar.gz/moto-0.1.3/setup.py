#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='moto',
    version='0.1.3',
    description='A library that allows your python tests to easily'
                ' mock out the boto library',
    author='Steve Pulec',
    author_email='spulec@gmail',
    url='https://github.com/spulec/moto',
    entry_points={
        'console_scripts': [
            'moto_server = moto.server:main',
        ],
    },
    packages=find_packages(),
    install_requires=[
        "boto",
        "Jinja2",
        "flask",
    ],
)
