#! /usr/bin/env python
from setuptools import setup, find_packages

setup(
        name='socketqueue',
        version='0.1.6',
        author='Marcelo Aires Caetano',
        author_email='marcelo@fiveti.com',
        license='BSD',
        keywords='epool kqueue select iocp',
        description='crossplatform Abastraction Interface to epool, kqueue, select, pool and IOCP(someday)',
        long_description=open('README.txt').read(),
        packages=find_packages(),
        url='http://github.com/caetanus/socketqueue'
        )
