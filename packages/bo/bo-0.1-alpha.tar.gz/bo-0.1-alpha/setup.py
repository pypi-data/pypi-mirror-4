#!/usr/bin/env python
from setuptools import setup, find_packages

from bo import __version__ as bo_version


def requirements():
    with open('requirements.txt') as f:
        return [line.strip() for line in f if not line.startswith('#')]

setup(
    name='bo',
    description='A simple, multi-protocol, extendable and embeddable chatbot',
    long_description=open('README.rst').read(),
    version=bo_version,
    author='Nikos Kokolakis',
    author_email='kokolakisnikos@gmail.com',
    url='http://bitbucket.org/konikos/bo',
    license='BSD style, see the included LICENSE file for details',
    packages=find_packages(),
    install_requires=requirements(),

    entry_points={
        'console_scripts': [
            'bo = bo.main:main',
        ]
    },

    test_suite='nose.collector',
    tests_require=['nose>=1.2.1'],

    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Topic :: Communications',
        ],
)
