#!/usr/bin/env python3

from distutils.core import setup

setup(name='blitz',
    version='0.3.3',
    author='Guilherme Hermeto',
    author_email='guilherme.hermeto@spirent.com',
    url='http://blitz.io',
    description='blitz.io python API client',
    package_dir={'': 'src'},
    packages=['blitz'],
    py_modules = ['blitz.api', 'blitz.sprint', 'blitz.rush', 'blitz.validation', 'blitz.curl'],
    keywords='blitz performance load test sprint rush ping',
    license='The MIT Licence',
    classifiers=['Operating System :: OS Independent',
               'Programming Language :: Python :: 3',
               'Programming Language :: Python :: 2.7',
               'Topic :: Software Development :: Testing :: Traffic Generation']
    )
