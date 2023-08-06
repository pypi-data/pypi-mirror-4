#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

version = "0.1.0"

def read(filename):
    import os.path
    return open(os.path.join(os.path.dirname(__file__), filename)).read()
setup(
    name="histogramy",
    version=version,
    description = "A small program to analysis 1 dimensional data",
    long_description=read('README.md'),
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    keywords = "1-dimensional, analysis, histogram",
    author = "Alisue",
    author_email = "lambdalisue@hashnote.net",
    url=r"https://github.com/lambdalisue/hisy",
    download_url = r"https://github.com/lambdalisue/hisy/tarball/master",
    license = 'MIT',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe = True,
    install_requires=[
        'setuptools',
        'numpy', 'matplotlib',
        'scikit-learn',
    ],
    entry_points={
        'console_scripts': [
            'histogramy = histogramy.main:main',
        ],
    },
)
