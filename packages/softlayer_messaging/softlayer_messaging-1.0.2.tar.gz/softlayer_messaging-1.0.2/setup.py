#!/usr/bin/python
from setuptools import setup, find_packages
import os

description = 'SoftLayer Message Queue Client'
long_description = description

if os.path.exists('README.md'):
    long_description = open('README.md').read()

setup(
    name='softlayer_messaging',
    version='1.0.2',
    description=description,
    long_description=long_description,
    url='http://sldn.softlayer.com/reference/messagequeueapi',
    author='Kevin McDonald',
    author_email='kmcdonald@softlayer.com',
    license='The BSD License',
    install_requires=['requests'],
    tests_require=['nose', 'mock'],
    packages=find_packages(exclude=['tests', 'ez_setup', 'examples']),
    test_suite='nose.collector',
    package_data={
        'softlayer_messaging': ['resources/config.json'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Intended Audience :: Developers',
        'Topic :: Communications',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Networking',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
