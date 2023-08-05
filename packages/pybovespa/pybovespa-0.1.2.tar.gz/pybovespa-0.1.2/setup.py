#!/usr/bin/env python
# Copyright (c) 2012 Beraldo Costa Leal <beraldo@beraldoleal.com>
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

try:
    from setuptools import setup
    extra = dict(test_suite="tests.test.suite", include_package_data=True)
except ImportError:
    from distutils.core import setup
    extra = {}

import sys

if sys.version_info <= (3, 2):
    error = "ERROR: pybovespa requires Python Version 3.2 or above...exiting."
    print >> sys.stderr, error
    sys.exit(1)

setup(name = "pybovespa",
      version = "0.1.2",
      description = "pybovespa is a basic library to get Bovespa stock values.",
      long_description = open("README").read(),
      author = "Beraldo Leal",
      author_email = "beraldo@beraloleal.com",
      url = "http://gitorious.org/unix-stuff/pybovespa",
      packages = ["pybovespa",],
      license = "MIT",
      platforms = "Posix; MacOS X;",
      classifiers = ["Development Status :: 2 - Pre-Alpha",
                     "Intended Audience :: Developers",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: POSIX",
                     "Topic :: Software Development :: Libraries :: Python Modules",
                     "Topic :: Internet",
                     "Programming Language :: Python :: 3.2"],
      **extra
      )
