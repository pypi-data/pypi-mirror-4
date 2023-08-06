# -*- coding: utf-8 -*-

# Copyright 2013 Vincent Jacques
# vincent@vincent-jacques.net

# This file is part of MockMockMock. http://jacquev6.github.com/MockMockMock

# MockMockMock is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# MockMockMock is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with MockMockMock.  If not, see <http://www.gnu.org/licenses/>.

from OrderingPolicies import OrderedOrderingPolicy, UnorderedOrderingPolicy
from CompletionPolicies import AllCompletionPolicy, AnyCompletionPolicy, RepeatedCompletionPolicy, ExactlyOneCompletionPolicy


class ExpectationWrapper(object):
    def __init__(self, expectation):
        self.__expectation = expectation
        self.__parent = None
        self.__called = False

    @property
    def name(self):
        return self.__expectation.name

    def expectsCall(self):
        return self.__expectation.expectsCall()

    def checkCall(self, args, kwds):
        return self.__expectation.checkCall(args, kwds)

    def checkName(self, name):
        return self.__expectation.checkName(name)

    def setParent(self, parent):
        assert(self.__parent is None)
        self.__parent = parent

    def getCurrentPossibleExpectations(self):
        if self.__called:
            return []
        else:
            return [self]

    def requiresMoreCalls(self):
        if self.__called:
            return False
        else:
            return True

    def getRequiredCallsExamples(self):
        return [self.__expectation.name]

    @property
    def called(self):
        return self.__called

    def call(self):
        self.__called = True
        self.__parent.markExpectationCalled(self)
        return self.__expectation.call(), self.__parent.rewindGroups()

    def resetCall(self):
        self.__called = False


class ExpectationGroup:
    def __init__(self, ordering, completion, sticky):
        self.__ordering = ordering
        self.__completion = completion
        self.__sticky = sticky
        self.__parent = None
        self.__expectations = []

    def setParent(self, parent):
        assert(self.__parent is None)
        self.__parent = parent

    @property
    def parent(self):
        assert(self.__parent is not None)
        return self.__parent

    def addExpectation(self, expectation):
        wrapper = ExpectationWrapper(expectation)
        wrapper.setParent(self)
        self.__expectations.append(wrapper)

    def addGroup(self, group):
        group.setParent(self)
        self.__expectations.append(group)

    def getCurrentPossibleExpectations(self):
        if self.__completion.acceptsMoreCalls(self.__expectations):
            return self.__ordering.getCurrentPossibleExpectations(self.__expectations)
        else:
            return []

    def requiresMoreCalls(self):
        return self.__completion.requiresMoreCalls(self.__expectations)

    def getRequiredCallsExamples(self):
        return self.__completion.getRequiredCallsExamples(self.__expectations)

    def rewindGroups(self):
        if self.__shallStick():
            return self
        else:
            return self.__parent.rewindGroups()

    def __shallStick(self):
        if self.__parent is None:
            return True
        if self.__sticky:
            return len(self.getCurrentPossibleExpectations()) != 0
        return False

    def markExpectationCalled(self, expectation):
        self.__completion.markExpectationCalled(self.__expectations, expectation)

    def resetCall(self):
        for e in self.__expectations:
            e.resetCall()


def makeGroup(ordering, completion, sticky):
    class Group(ExpectationGroup):
        def __init__(self):
            ExpectationGroup.__init__(self, ordering(), completion(), sticky)

    return Group


OrderedExpectationGroup = makeGroup(OrderedOrderingPolicy, AllCompletionPolicy, False)
UnorderedExpectationGroup = makeGroup(UnorderedOrderingPolicy, AllCompletionPolicy, False)
AtomicExpectationGroup = makeGroup(OrderedOrderingPolicy, AllCompletionPolicy, True)
OptionalExpectationGroup = makeGroup(OrderedOrderingPolicy, AnyCompletionPolicy, False)
AlternativeExpectationGroup = makeGroup(UnorderedOrderingPolicy, ExactlyOneCompletionPolicy, False)
RepeatedExpectationGroup = makeGroup(OrderedOrderingPolicy, RepeatedCompletionPolicy, False)
