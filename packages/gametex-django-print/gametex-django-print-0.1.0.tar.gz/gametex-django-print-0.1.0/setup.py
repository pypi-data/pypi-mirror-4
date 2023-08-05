# coding=utf-8
"""
Setup file.
"""
from distutils.core import setup
from setuptools import find_packages

setup(
    name='gametex-django-print',
    version='0.1.0',
    packages=find_packages(),
    author='Christian Ternus',
    author_email='ternus@cternus.net',
    url='http://github.com/ternus/gametex-print',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    description='Generate PDFs from GameTeX in Django',
    long_description=open('README.md').read(),
    install_requires=['Django'],
)
