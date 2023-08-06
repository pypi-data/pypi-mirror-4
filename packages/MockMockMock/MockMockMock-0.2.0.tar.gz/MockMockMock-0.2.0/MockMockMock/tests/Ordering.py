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


class Ordering(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.mocks = MockMockMock.Engine()
        self.myMock = self.mocks.create("myMock")

    def testUnorderedGroupOfSameMethod(self):
        with self.mocks.unordered:
            self.myMock.expect.foobar(1).andReturn(11)
            self.myMock.expect.foobar(1).andReturn(13)
            self.myMock.expect.foobar(2).andReturn(12)
            self.myMock.expect.foobar(1).andReturn(14)
        self.assertEqual(self.myMock.object.foobar(2), 12)
        self.assertEqual(self.myMock.object.foobar(1), 11)
        self.assertEqual(self.myMock.object.foobar(1), 13)
        self.assertEqual(self.myMock.object.foobar(1), 14)
        self.mocks.tearDown()

    ### @todo Allow unordered property and method calls on the same name: difficult
    def testUnorderedGroupOfSameMethodAndProperty(self):
        with self.assertRaises(MockMockMock.Exception) as cm:
            with self.mocks.unordered:
                self.myMock.expect.foobar()
                self.myMock.expect.foobar
            self.myMock.object.foobar
        self.assertEqual(cm.exception.message, "myMock.foobar is expected as a property and as a method call in an unordered group")

    def testUnorderedGroupOfSamePropertyAndMethod(self):
        with self.assertRaises(MockMockMock.Exception) as cm:
            with self.mocks.unordered:
                self.myMock.expect.foobar
                self.myMock.expect.foobar()
            self.myMock.object.foobar()
        self.assertEqual(cm.exception.message, "myMock.foobar is expected as a property and as a method call in an unordered group")
