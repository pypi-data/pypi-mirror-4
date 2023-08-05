#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import ParsePkgtxt


setup(
    name='ParsePkgtxt',
    version=ParsePkgtxt.__version__,

    # find packages if any
    packages=find_packages(),

    author="Frédéric Galusik",
    author_email="fred.galusik at gmail",
    description="Parse a Slackware PACKAGES.TXT and build a dictionnary",
    license="BSD revised",    
    long_description=open('README.rst').read(),

    # install_requires=Ex: ["foo", "bar >= 0.1", "foobar==0.2"] ,

    # Active manifest.in
    include_package_data=True,

    # HomePage
    url='http://github.com/fredg/ParsePkgtxt',

    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Utilities",
    ],
)
