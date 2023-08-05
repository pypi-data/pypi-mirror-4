#!/usr/bin/env python
from distutils.core import setup

setup(
    name='MetOffer',
    version='0.1',
    author='Stephen B. Murray',
    author_email='sbm199 WITH gmail STOP com',
    py_modules=['metoffer'],
    url='http://pypi.python.org/pypi/MetOffer/',
    license='LICENSE.txt',
    description='Simple wrapper for the Met Office datapoint API.',
    long_description=open('README.txt').read(),
)