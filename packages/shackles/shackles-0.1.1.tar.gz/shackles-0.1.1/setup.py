#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import shackles

setup(
    name='shackles',
    version='0.1.1',
    author='Justin Barber',
    author_email='barber.justin@gmail.com',
    description='Recursive attribute tools.',
    long_description=open('README.rst').read(),
    license="MIT",
    url='https://github.com/barberj/shackles',
    package_data={'shackles':["README.rst"]},
    py_modules=["shackles"],
    classifiers=(
        'License :: OSI Approved :: MIT License',
        "Development Status :: 5 - Production/Stable",
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        "Topic :: Utilities",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
    ),
)
