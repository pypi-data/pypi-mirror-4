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


groupMakers = {
    "o": lambda f: f.ordered,
    "u": lambda f: f.unordered,
    "a": lambda f: f.atomic,
    "p": lambda f: f.optional,
    "l": lambda f: f.alternative,
    "r": lambda f: f.repeated,
}


def makeExpectations(mocks, mock, groups):
    if len(groups) > 0:
        group = groups[0]
        with groupMakers[group](mocks):
            mock.expect.foobar(group + "A")
            mock.expect.foobar(group + "B")
            makeExpectations(mocks, mock, groups[1:])
            mock.expect.foobar(group + "C")
            mock.expect.foobar(group + "D")


def testAllowedOrder(allowedOrder):
    def test(self):
        for argument in allowedOrder:
            self.call(argument)
        self.mocks.tearDown()
    return test


def testForbidenOrder(forbidenOrder):
    def test(self):
        for argument in forbidenOrder[: -1]:
            self.call(argument)
        with self.assertRaises(MockMockMock.Exception):
            self.call(forbidenOrder[-1])
    return test


def testTearDownError(forbidenOrder):
    def test(self):
        for argument in forbidenOrder:
            self.call(argument)
        with self.assertRaises(MockMockMock.Exception):
            self.mocks.tearDown()
    return test


def makeTestCase(groups, allowedOrders, forbidenOrders, tearDownErrors):
    groups = list(groups)
    allowedOrders = [
        [
            allowedOrder[2 * i:2 * i + 2]
            for i in range(len(allowedOrder) // 2)
        ]
        for allowedOrder in allowedOrders
    ]
    forbidenOrders = [
        [
            forbidenOrder[2 * i:2 * i + 2]
            for i in range(len(forbidenOrder) // 2)
        ]
        for forbidenOrder in forbidenOrders
    ]
    tearDownErrors = [
        [
            tearDownError[2 * i:2 * i + 2]
            for i in range(len(tearDownError) // 2)
        ]
        for tearDownError in tearDownErrors
    ]

    class TestCase(unittest.TestCase):
        def setUp(self):
            unittest.TestCase.setUp(self)
            self.mocks = MockMockMock.Engine()
            self.myMock = self.mocks.create("myMock")
            makeExpectations(self.mocks, self.myMock, groups)

        def call(self, argument):
            assert(len(argument) == 2)
            assert(argument[0] in groupMakers)
            assert(argument[1] in "ABCDX")
            self.myMock.object.foobar(argument)

    for allowedOrder in allowedOrders:
        setattr(TestCase, "test_" + "".join(allowedOrder), testAllowedOrder(allowedOrder))

    for forbidenOrder in forbidenOrders:
        setattr(TestCase, "test_" + "".join(forbidenOrder), testForbidenOrder(forbidenOrder))

    for tearDownError in tearDownErrors:
        setattr(TestCase, "test_" + "".join(tearDownError), testTearDownError(tearDownError))

    TestCase.__name__ = "TestCase_" + "".join(groups)

    return TestCase

UnorderedGroup = makeTestCase(
    "u",
    [
        # Completed in any order
        "uAuBuCuD",
        "uBuAuDuC",
        "uBuCuAuD",
    ],
    [
        # Bad argument
        "uAuX",
    ],
    [
        # Not completed
        "uAuBuC",
        "uAuBuD",
        "uAuB",
        "uA",
        "",
    ]
)

OrderedGroup = makeTestCase(
    "o",
    [
        # Completed in good order
        "oAoBoCoD",
    ],
    [
        # Wrong order
        "oB",
        "oC",
        "oD",
    ],
    [
        # Not completed
        "oAoBoC",
        "oAoB",
        "oA",
        "",
    ]
)

OptionalGroup = makeTestCase(
    "p",
    [
        # Completed in good order
        "pApBpCpD",
        # Not completed
        "pApBpC",
        "pApB",
        "pA",
        "",
    ],
    [
        # Wrong order
        "pB",
    ],
    [
    ]
)

AlternativeGroup = makeTestCase(
    "l",
    [
        # One call
        "lA",
        "lB",
        "lC",
        "lD",
    ],
    [
        # Two calls
        "lAlB",
        "lBlA",
    ],
    [
        # No call
        "",
    ]
)

RepeatedGroup = makeTestCase(
    "r",
    [
        # Zero call
        "",
        # One time
        "rArBrCrD",
        # Several times
        "rArBrCrDrArBrCrD",
        "rArBrCrDrArBrCrDrArBrCrD",
    ],
    [
    ],
    [
        # Partial calls
        "rA",
        "rArB",
        "rArBrCrDrA",
        "rArBrCrDrArB",
        "rArBrCrDrArBrCrDrA",
        "rArBrCrDrArBrCrDrArB",
    ]
)

OrderedInUnorderedGroup = makeTestCase(
    "uo",
    [
        # Original order
        "uAuBoAoBoCoDuCuD",
        # Other possible orders
        #  ordered group at once
        "oAoBoCoDuAuBuCuD",
        "uAuBuCuDoAoBoCoD",
        #  ordered group in pieces
        "oAuAoBuBoCuCoDuD",
        "oAuDoBuCoCuBoDuA",
    ],
    [
        # Ordered group in wrong order
        "uAuBoB",
    ],
    [
    ]
)

AtomicInUnorderedGroup = makeTestCase(
    "ua",
    [
        # Original order
        "uAuBaAaBaCaDuCuD",
        # Other possible orders
        #  atomic group at once
        "aAaBaCaDuAuBuCuD",
        "uAuBuCuDaAaBaCaD",
    ],
    [
        # Atomic group in wrong order
        "uAuBaB",
        # Atomic group in pieces
        "uAaAuB",
    ],
    [
    ]
)

UnorderedInRepeatedGroup = makeTestCase(
    "ru",
    [
        "",
        "rArBuAuBuCuDrCrD",
        "rArBuAuBuCuDrCrDrArBuAuBuCuDrCrD",
    ],
    [
        # Partial
        "rArBuAuBuCrC",
    ],
    [
        # Partial
        "rArBuAuBuCuDrC",
    ]
)
