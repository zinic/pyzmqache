# -*- coding: utf-8 -*-
import sys
import os

from setuptools import setup, find_packages

def read(relative):
    contents = open(relative, 'r').read()
    return [l for l in contents.split('\n') if l != '']

setup(
    name='pyzmqache',
    version=read('VERSION')[0],
    description='Embedable cache for Python using ZeroMQ transports .',
    author='John Hopper',
    author_email='john.hopper@jpserver.net',
    url='https://github.com/zinic/pyzmqache',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Cython',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet',
        'Topic :: Utilities'
    ],
    tests_require=read('./tools/tests-require'),
    install_requires=read('./tools/install-requires'),
    test_suite='nose.collector',
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(exclude=['*.tests']))
