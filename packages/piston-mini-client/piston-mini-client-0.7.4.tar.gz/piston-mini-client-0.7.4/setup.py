#!/usr/bin/env python

from setuptools import setup

setup(name='piston-mini-client',
    version='0.7.4',
    description='A package to consume Django-Piston web services',
    url='https://launchpad.net/piston-mini-client',
    author='Anthony Lenton',
    author_email='anthony.lenton@canonical.com',
    packages=['piston_mini_client'],
    license='LGPLv3',
    install_requires=[
        'oauthlib',
        'httplib2',
    ],
    test_suite = 'nose.collector',
    )
