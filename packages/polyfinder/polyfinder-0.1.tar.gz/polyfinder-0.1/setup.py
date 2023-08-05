#!/usr/bin/env python

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="polyfinder",
    version="0.1",
    description="",
    author="Joseph R. Tricarico",
    author_email="jtricarico@gmail.com",
    url="http://github.com/joetric/polyfinder",
    license="MIT",
    long_description=read('README.rst'),
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering :: GIS',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=['python-omgeo==1.4.4'],
    #test_suite='polyfinder.tests.tests',
)
