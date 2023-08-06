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


class SingleExpectationNotCalled(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.mocks = MockMockMock.Engine()
        self.myMock = self.mocks.create("myMock")

    def testMethodCallWithBadArgument(self):
        self.myMock.expect.foobar(42)
        with self.assertRaises(MockMockMock.Exception) as cm:
            self.myMock.object.foobar(43)
        self.assertEqual(cm.exception.message, "myMock.foobar called with bad arguments (43,) {}")

    def testMethodCallWithBadName(self):
        self.myMock.expect.foobar()
        with self.assertRaises(MockMockMock.Exception) as cm:
            self.myMock.object.barbaz()
        self.assertEqual(cm.exception.message, "myMock.barbaz called instead of myMock.foobar")

    def testPropertyWithBadName(self):
        self.myMock.expect.foobar.andReturn(42)
        with self.assertRaises(MockMockMock.Exception) as cm:
            self.myMock.object.barbaz
        self.assertEqual(cm.exception.message, "myMock.barbaz called instead of myMock.foobar")

    def testMethodNotCalled(self):
        self.myMock.expect.foobar()
        with self.assertRaises(MockMockMock.Exception) as cm:
            self.mocks.tearDown()
        self.assertEqual(cm.exception.message, "myMock.foobar not called")
        self.myMock.object.foobar()
        self.mocks.tearDown()

    def testPropertyNotCalled(self):
        self.myMock.expect.foobar
        with self.assertRaises(MockMockMock.Exception) as cm:
            self.mocks.tearDown()
        self.assertEqual(cm.exception.message, "myMock.foobar not called")
        self.myMock.object.foobar
        self.mocks.tearDown()

    # def testPropertyNotCalledInOrderedGroup(self):
    #     self.myMock.expect.foobar
    #     self.myMock.expect.barbaz
    #     with self.assertRaises(MockMockMock.Exception) as cm:
    #         self.mocks.tearDown()
    #     self.assertEqual(cm.exception.message, "myMock.foobar not called")
    #     self.myMock.object.foobar
    #     with self.assertRaises(MockMockMock.Exception) as cm:
    #         self.mocks.tearDown()
    #     self.assertEqual(cm.exception.message, "myMock.barbaz not called")
    #     self.myMock.object.barbaz
    #     self.mocks.tearDown()

    # def testPropertyNotCalledInUnorderedGroup(self):
    #     with self.mocks.unordered:
    #         self.myMock.expect.foobar
    #         self.myMock.expect.barbaz
    #     with self.assertRaises(MockMockMock.Exception) as cm:
    #         self.mocks.tearDown()
    #     self.assertEqual(cm.exception.message, "myMock.foobar or myMock.barbaz not called")
    #     self.myMock.object.foobar
    #     with self.assertRaises(MockMockMock.Exception) as cm:
    #         self.mocks.tearDown()
    #     self.assertEqual(cm.exception.message, "myMock.barbaz not called")
    #     self.myMock.object.barbaz
    #     self.mocks.tearDown()
