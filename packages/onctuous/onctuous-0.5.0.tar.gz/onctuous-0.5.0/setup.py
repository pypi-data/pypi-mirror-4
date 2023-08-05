# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Alec Thomas <alec@swapoff.org>
# Copyright (C) 2012 Jean-Tiare Le Bigot <jtlebigot@socialludia.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: Jean-Tiare Le Bigot <jtlebigot@socialludia.com>

from setuptools import setup, find_packages

install_requires = [
    'd2to1',
    'setuptools >= 0.6b1',
]

tests_requires = [
    'nose',
    'nosexcover',
    'coverage',
    'mock',
    'webtest',
]

setup(
    d2to1=True,
    keywords='validation',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_requires,
    test_suite="tests",
)
