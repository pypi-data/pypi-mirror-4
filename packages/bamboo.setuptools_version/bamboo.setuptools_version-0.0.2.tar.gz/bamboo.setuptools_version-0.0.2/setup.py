#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###  
# Copyright (c) Rice University 2012
# This software is subject to
# the provisions of the GNU Lesser General
# Public License Version 2.1 (LGPL).
# See LICENCE.txt for details.
###


'''
setup.py for bamboo

'''
from setuptools import setup, find_packages
import os

#The best way to solve the chiken and egg problem for now
version = '0.0.2'


setup(
    name='bamboo.setuptools_version',
    version=version,
    description="Tiny package to dop just one things -0 solve gettng a vfersion number for a package",
    packages=find_packages(),
    namespace_packages=['bamboo'],
    author='See AUTHORS.txt',
    author_email='info@cnx.org',
    url='https://github.com/Connexions/bamboo.setuptools_version',
    license='LICENSE.txt'
    )
