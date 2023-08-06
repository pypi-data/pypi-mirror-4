# -*- coding: utf-8 -*-
'''
Created on Mar 23, 2013

@author: vahid
'''
import os
import re
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# reading easystate version (same way sqlalchemy does)
with open(os.path.join(os.path.dirname(__file__), 'easystate', '__init__.py')) as v_file:
    package_version = re.compile(r".*__version__ = ['\"](.*?)['\"]", re.S).match(v_file.read()).group(1)

dependencies = []

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="easystate",
    version=package_version,
    author="Vahid Mardani",
    author_email="vahid.mardani@gmail.com",
    url="https://github.com/pylover/easystate",
    description="Python State-Machine library",
    maintainer="Vahid Mardani",
    maintainer_email="vahid.mardani@gmail.com",
    packages=["easystate"],
    platforms=["any"],
    long_description=read('README.txt'),
    install_requires=dependencies,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: Freeware",
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries'
    ]
)
