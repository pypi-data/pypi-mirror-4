#!/usr/bin/env python

# Copyright 2011-2013 Arthur Noel
#
# This file is part of Yanc.
#
# Yanc is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Yanc is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Yanc. If not, see <http://www.gnu.org/licenses/>.

import os

from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), "README.rst")).read()

# under test we do not want the nose entry point installed because it screws up
# coverage since the package is imported too early
if "YANC_NO_NOSE" in os.environ:
    entry_points = None
else:
    entry_points = {
        "nose.plugins": ("yanc=yanc.yancplugin:YancPlugin",),
        }

setup(name="yanc",
      version="0.2.4",
      description="Yet another nose colorer",
      long_description=README,
      license="GPL",
      keywords="nose color",
      author="Arthur Noel",
      author_email="arthur@0compute.net",
      url="https://github.com/0compute/yanc",
      packages=("yanc",),
      entry_points=entry_points,
      )
