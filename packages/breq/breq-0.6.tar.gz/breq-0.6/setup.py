#!/usr/bin/env python
# coding: utf-8
import os
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='breq',
    version='0.6',
    packages=find_packages(),
    include_package_data=True,
    install_requires=required,
    long_description=open('README.rst').read(),
    license='MIT',
    author='Ramiro Gómez',
    author_email='code@ramiro.org',
    description='Browse Web service requests.',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Communications",
        "Topic :: Text Processing",
    ]
)