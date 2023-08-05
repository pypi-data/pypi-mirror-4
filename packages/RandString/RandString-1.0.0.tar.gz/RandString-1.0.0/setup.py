#!/usr/bin/python3.2

from distutils.core import setup

setup(
    name='RandString',
    version='1.0.0',
    author='Ryan Porterfield',
    author_email='ryan@ryanporterfield.com',
    scripts=["bin/passgen.py",],
    url='http://pypi.python.org/pypi/RandString/',
    license='LICENSE.txt',
    description='Python3 module for generating randomized strings',
    long_description=open( 'README.txt' ).read(),
)
