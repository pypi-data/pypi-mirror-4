#!/usr/bin/env python
# -*- coding: utf-8

from setuptools import setup

setup(
    name='tornado-foursquare',
    version='0.0.2',
    license='OSI',
    description='A tornado based foursquare api wrapper',
    author='Rafael Soares',
    author_email='rafaelsantos88@gmail.com',
    url='https://github.com/rafaels88/tornado-foursquare',
    packages=['foursquare'],
    long_description=open('README.md').read(),
    install_requires=open("requirements.txt").read().split("\n"),
)
