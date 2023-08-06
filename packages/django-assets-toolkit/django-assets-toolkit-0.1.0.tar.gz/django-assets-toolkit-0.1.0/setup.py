#!/usr/bin/env python

import os
import sys
import assetstoolkit
from setuptools import setup, find_packages


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist register upload')
    sys.exit()

packages = ['assetstoolkit']
requires = ['pyScss==1.1.4',
            'CoffeeScript==1.0.5']

setup(
    name=assetstoolkit.__title__,
    version=assetstoolkit.__version__,
    packages=find_packages(),
    license=open('LICENSE.txt').read(),
    description='A development toolkit for compiling sass and coffee script files.',
    long_description=open('README.rst').read(),
    author='Marconi Moreto',
    author_email='caketoad@gmail.com',
    url='https://github.com/pypug/django-assets-toolkit',
    zip_safe=False,
    package_data={'': ['LICENSE.txt']},
    install_requires=requires
)
