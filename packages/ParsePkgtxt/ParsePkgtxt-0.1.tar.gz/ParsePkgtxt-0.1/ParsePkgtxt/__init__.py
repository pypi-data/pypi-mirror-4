#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
"""
    This class read and parse a Slackware Linux PACKAGES.TXT file and build
    a dictionnary which contains all packages names as keys and all detailed 
    informations about the packages as values (version, arch, release, 
    dependancies, location, sizes, slackdesc).
"""
 
__version__ = "0.1"
 
from parsepkgtxt import Package
