# -*- coding: utf-8 -*-

# Copyright 2013 Vincent Jacques
# vincent@vincent-jacques.net

# This file is part of MockMockMock. http://jacquev6.github.com/MockMockMock

# MockMockMock is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# MockMockMock is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with MockMockMock.  If not, see <http://www.gnu.org/licenses/>.


class AllCompletionPolicy:
    def requiresMoreCalls(self, expectations):
        for expectation in expectations:
            if expectation.requiresMoreCalls():
                return True
        return False

    def getRequiredCallsExamples(self, expectations):
        required = []
        for expectation in expectations:
            if expectation.requiresMoreCalls():
                required += expectation.getRequiredCallsExamples()
        return required

    def acceptsMoreCalls(self, expectations):
        return any(len(expectation.getCurrentPossibleExpectations()) != 0 for expectation in expectations)

    def markExpectationCalled(self, expectations, expectation):
        pass


class AnyCompletionPolicy:
    def requiresMoreCalls(self, expectations):
        return False

    def acceptsMoreCalls(self, expectations):
        return True

    def markExpectationCalled(self, expectations, expectation):
        pass


class ExactlyOneCompletionPolicy:
    def requiresMoreCalls(self, expectations):
        for expectation in expectations:
            if not expectation.requiresMoreCalls():
                return False
        return True

    def getRequiredCallsExamples(self, expectations):
        return []

    def acceptsMoreCalls(self, expectations):
        return self.requiresMoreCalls(expectations)

    def markExpectationCalled(self, expectations, expectation):
        pass


class RepeatedCompletionPolicy:
    def requiresMoreCalls(self, expectations):
        required = 0
        if expectations[0].called:
            for expectation in expectations:
                required += expectation.requiresMoreCalls()
        return required

    def getRequiredCallsExamples(self, expectations):
        return []

    def acceptsMoreCalls(self, expectations):
        return True

    def markExpectationCalled(self, expectations, expectation):
        if expectation is expectations[-1]:
            for e in expectations:
                e.resetCall()
