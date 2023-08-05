#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''setup for knife'''

from os import getcwd
from os.path import join

from setuptools import setup, find_packages


def getversion(fname):
    '''
    Get the __version__ without importing.
    '''
    for line in open(fname):
        if line.startswith('__version__'):
            return '%s.%s.%s' % eval(line[13:])

setup(
    name='knife',
    version=getversion('knife/__init__.py'),
    description='Things go in. Things get knifed. Things go out.',
    long_description=open(join(getcwd(), 'README.rst'), 'r').read(),
    keywords='pipeline filtering chaining iterator functional fluent chaining',
    license='BSD',
    author='L. C. Rees',
    author_email='lcrees@gmail.com',
    url='https://bitbucket.org/lcrees/knife',
    packages=find_packages(),
    test_suite='knife.tests',
    zip_safe=False,
    install_requires=list(l.strip() for l in open(
        join(getcwd(), 'reqs/requires.txt'), 'r',
    ).readlines()),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
)
