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

from setuptools import setup

setup_requires = [
    'd2to1',
    'nose',
    'nosexcover',
    'coverage',
    'mock',
]

setup(
    d2to1=True,
    keywords='validation',
    include_package_data=True,
    zip_safe=False,
    setup_requires=setup_requires,
    test_suite="nose.collector",
)
