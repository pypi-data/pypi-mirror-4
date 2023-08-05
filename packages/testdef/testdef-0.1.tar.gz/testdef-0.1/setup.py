#!/usr/bin/env python
#
# Copyright (C) 2012 Canonical
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
#
# This file is part of testdef.
#
# testdef is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# testdef is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with testdef.  If not, see <http://www.gnu.org/licenses/>.


from setuptools import setup, find_packages


setup(
    name='testdef',
    version='0.1',
    author="Zygmunt Krynicki",
    author_email="zygmunt.krynicki@canonical.com",
    packages=find_packages(),
    test_suite='testdef.tests',
    description=("Testdef is an emerging test definition interchange intended"
                 " for storing and describing tests in a public repository."),
    url='https://github.com/zyga/testdef',
    use_2to3=True,
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        ("License :: OSI Approved :: GNU Library or Lesser General Public"
         " License (LGPL)"),
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Topic :: Software Development :: Testing"
    ],
    zip_safe=True)
