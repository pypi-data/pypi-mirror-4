#-*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages
import basitapi

def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''

setup(
    name='basitapi',
    version=basitapi.__version__,
    description=read('DESCRIPTION'),
    long_description=read('README.md'),
    licence='The MIT LICENCE',
    platform=['OS Independent'],
    keywords='rest, api, django',
    author='Ömer ÜCEL',
    author_email='omerucel@gmail.com',
    url='https://github.com/omerucel/basitapi',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django',
    ],
    test_require=[
        'django-nose',
        'coverage',
        'fabric',
    ],
    test_suite='basitapi.tests.runtests.runtests',
)
