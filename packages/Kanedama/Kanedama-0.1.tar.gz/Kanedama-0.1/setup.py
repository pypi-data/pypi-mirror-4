#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

install_requires = ['Ghost.py']

try:
    import argparse
except ImportError:
    install_requires.append('argparse')

setup(
    name='Kanedama',
    version='0.1',
    provides=['kanedama'],
    description='Download and email Heroku invoices',
    long_description=open('README.rst').read(),
    author='James Rutherford',
    author_email='jim@jimr.org',
    url='https://github.com/jimr/Kanedama',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: PyPy',
        ],
    license='MIT',
    test_suite='tests',
    scripts=['kanedama.py'],
    py_modules=['kanedama'],
    install_requires=install_requires,
)
