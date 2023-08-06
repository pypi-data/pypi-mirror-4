#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 Vincent Jacques
# vincent@vincent-jacques.net

# This file is part of MockMockMock. http://jacquev6.github.com/MockMockMock

# MockMockMock is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# MockMockMock is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with MockMockMock.  If not, see <http://www.gnu.org/licenses/>.

import setuptools
import textwrap

version = "0.2.0"


if __name__ == "__main__":
    setuptools.setup(
        name="MockMockMock",
        version=version,
        description="My mock library. Don't use it (yet)",
        author="Vincent Jacques",
        author_email="vincent@vincent-jacques.net",
        url="http://jacquev6.github.com/MockMockMock",
        long_description=textwrap.dedent("""\
        """),
        packages=[
            "MockMockMock",
            "MockMockMock._Details",
            "MockMockMock._Details.ExpectationGrouping",
            "MockMockMock.tests",
        ],
        package_data={
            "MockMockMock": ["COPYING*"],
        },
        classifiers=[
            "Development Status :: 2 - Pre-Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Topic :: Software Development",
        ],
        test_suite="MockMockMock.tests.AllTests",
        use_2to3=True
    )
