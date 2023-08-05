#!/usr/bin/python
#===============================================================================
# Copyright (C) 2012 Adrian Hungate
#
# Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#===============================================================================
"""
This file is part of PyMMB - The crossplatform MMB library and toolset
If you don't use MMC Flash cards in a BBC Microcomputer, this is unlikely
to be a lot of use to you!
"""

from setuptools import setup
from PyMMB import version

readme = open('README.rst').read()
changes = open('CHANGES.rst').read()

setup(
    name = "PyMMB",
    version = str(version),
    description = "Python library for accessing BBC Microcomputer DFS disk images and MMB disk bundles",
    author = "Adrian Hungate",
    author_email = "adrian@tlspu.com",
    url = "http://projects.tlspu.com/PyMMB",
    requires = [],
    packages = ["PyMMB"],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: System :: Filesystems',
        'Topic :: Utilities',
    ],
    long_description = readme + "\n" + changes
)
