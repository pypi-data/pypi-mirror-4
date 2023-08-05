#!/usr/bin/env python

from setuptools import setup

setup(
    name='namedentities',
    version='1.3',
    author='Jonathan Eunice',
    author_email='jonathan.eunice@gmail.com',
    description='Converts numeric HTML entities and Unicode characters to nice, neat named HTML entities',
    long_description=open('README.rst').read(),
    url='http://bitbucket.org/jeunice/namedentities',
    packages=['namedentities'],
    install_requires=[],
    tests_require = ['tox', 'pytest','six'],
    zip_safe = True,
    keywords='HTML named entities numeric entities',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup :: HTML'
    ]
)
