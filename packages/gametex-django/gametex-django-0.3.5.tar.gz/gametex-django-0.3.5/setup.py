# coding=utf-8
"""
Setup file.
"""
from distutils.core import setup
from setuptools import find_packages

setup(
    name='gametex-django',
    version='0.3.5',
    packages=find_packages(),
    author='Christian Ternus',
    author_email='ternus@cternus.net',
    url='http://github.com/ternus/gametex-django',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    description='Django integration for GameTeX',
    long_description=open('README.md').read(),
    install_requires=['Django'],
)
