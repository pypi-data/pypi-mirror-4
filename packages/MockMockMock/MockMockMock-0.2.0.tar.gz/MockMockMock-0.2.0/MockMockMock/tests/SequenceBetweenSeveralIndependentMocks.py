# -*- coding: utf-8 -*-

# Copyright 2013 Vincent Jacques
# vincent@vincent-jacques.net

# This file is part of MockMockMock. http://jacquev6.github.com/MockMockMock

# MockMockMock is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# MockMockMock is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with MockMockMock.  If not, see <http://www.gnu.org/licenses/>.

import unittest

import MockMockMock


class SequenceBetweenSeveralIndependentMocks(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.mocks1 = MockMockMock.Engine()
        self.mocks2 = MockMockMock.Engine()
        self.m1 = self.mocks1.create("m1")
        self.m2 = self.mocks2.create("m2")

    def testSameOrderSequence(self):
        self.m1.expect.foobar(42)
        self.m2.expect.foobar(43)
        self.m1.object.foobar(42)
        self.m2.object.foobar(43)
        self.mocks1.tearDown()
        self.mocks2.tearDown()

    def testOtherOrderSequence(self):
        self.m1.expect.foobar(42)
        self.m2.expect.foobar(43)
        self.m2.object.foobar(43)
        self.m1.object.foobar(42)
        self.mocks1.tearDown()
        self.mocks2.tearDown()
