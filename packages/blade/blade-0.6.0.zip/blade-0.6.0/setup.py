#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''setup for blade'''

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
    name='blade',
    version=getversion('blade/__init__.py'),
    description='Powerful iterable processing tools extracted from knife.',
    long_description=open(join(getcwd(), 'README.rst'), 'r').read(),
    keywords='filtering iterator functional interable',
    license='BSD',
    author='L. C. Rees',
    author_email='lcrees@gmail.com',
    url='https://bitbucket.org/lcrees/blade',
    packages=find_packages(),
    test_suite='blade.tests',
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
)
