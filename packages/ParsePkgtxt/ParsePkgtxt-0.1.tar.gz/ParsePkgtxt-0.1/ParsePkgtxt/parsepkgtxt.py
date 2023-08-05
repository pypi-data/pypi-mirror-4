#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Frédéric Galusik <fredg~AT~salixos~org>
# License: BSD revised (see LICENSE for details).

"""
Read and parse a Slackware Linux PACKAGES.TXT file and build a
slackd dictionnary with package names as keys and packages detailed
informations as values.

Usage:

    >>> from ParsePkgtxt import Package
    >>> Package.parse(Package(), 'PACKAGES.TXT')
"""

import re


__all__ = ['Package']


class Package:
    """
    This class read and parse a Slackware Linux PACKAGES.TXT file and build
    a slackd dictionnary which contains all packages names as keys and all
    detailed informations about the packages as values (version, arch, release,
    dependancies, packages conflicts, packages suggested, location, sizes,
    slackdesc).
    """
    def __init__(self):
        """
        Initialize a New Package.
        """
        self.name = ''
        self.version = ''
        self.release = ''
        self.arch = ''
        self.deps = ''
        self.con = ''
        self.sug = ''
        self.location = ''
        self.sizec = ''
        self.sizeu = ''
        self.slackdesc = ''

    def parse(self, pkgtxtfile):
        """
        Parse the PACKAGES.TXT file given in argument and build the
        slackd dictionnary.
        """
        self.pkgtxtfile = pkgtxtfile
        self.pkg = Package()
        self.slackd = {}
        with open(pkgtxtfile) as f:
            for line in f:
                pkgline = re.match(
                    r'(PACKAGE NAME:\s\s)(.*)', line)
                locationline = re.match(
                    r'(PACKAGE LOCATION:\s\s\.)(.*)', line)
                depline = re.match(
                    r'(PACKAGE REQUIRED:\s\s)(.*)', line)
                conline = re.match(
                    r'(PACKAGE CONFLICTS:\s\s)(.*)', line)
                sugline = re.match(
                    r'(PACKAGE SUGGESTS:\s\s)(.*)', line)
                sizecline = re.match(
                    r'(PACKAGE\sSIZE\s\(compressed\):\s\s)(.*)', line)
                sizeuline = re.match(
                    r'(PACKAGE\sSIZE\s\(uncompressed\):\s\s)(.*)', line)
                slackdescline = re.match(
                    r'(%s:\s)(.*)' % self.pkg.name.replace('+', '\+'), line)
                emptyline = re.match(
                    r'^$', line)
                if pkgline:
                    pname = pkgline.group(2)
                    pname = re.match(
                        r'(.*)-([^-]*)-([^-]*)-([^-]*).t[glx]z$', pname)
                    self.pkg.name = pname.group(1)
                    self.pkg.version = pname.group(2)
                    self.pkg.arch = pname.group(3)
                    self.pkg.release = pname.group(4)
                if depline:
                    self.pkg.deps = depline.group(2)
                if conline:
                    self.pkg.con = conline.group(2)
                if sugline:
                    self.pkg.sug = sugline.group(2)
                if locationline:
                    self.pkg.location = locationline.group(2)
                if sizecline:
                    self.pkg.sizec = sizecline.group(2)
                if sizeuline:
                    self.pkg.sizeu = sizeuline.group(2)
                if slackdescline:
                    self.pkg.slackdesc += " " + slackdescline.group(2).\
                        replace('"', '\'').\
                        replace('&', 'and').\
                        replace('>', '').\
                        replace('<', '')
                if emptyline and self.pkg.name:
                    self.pkg.slackdesc = self.pkg.slackdesc.strip()
                    self.slackd.setdefault(
                        self.pkg.name, []).append(self.pkg.version)
                    self.slackd.setdefault(
                        self.pkg.name, []).append(self.pkg.arch)
                    self.slackd.setdefault(
                        self.pkg.name, []).append(self.pkg.release)
                    self.slackd.setdefault(
                        self.pkg.name, []).append(self.pkg.deps)
                    self.slackd.setdefault(
                        self.pkg.name, []).append(self.pkg.con)
                    self.slackd.setdefault(
                        self.pkg.name, []).append(self.pkg.sug)
                    self.slackd.setdefault(
                        self.pkg.name, []).append(self.pkg.location)
                    self.slackd.setdefault(
                        self.pkg.name, []).append(self.pkg.sizec)
                    self.slackd.setdefault(
                        self.pkg.name, []).append(self.pkg.sizeu)
                    self.slackd.setdefault(
                        self.pkg.name, []).append(self.pkg.slackdesc)
                    self.pkg = Package()
            return self.slackd
