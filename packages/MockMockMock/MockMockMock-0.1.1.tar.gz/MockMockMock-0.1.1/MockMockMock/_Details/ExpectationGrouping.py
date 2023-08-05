class OrderedOrderingPolicy:
    def getCurrentPossibleExpectations( self, expectations ):
        possible = []
        for expectation in expectations:
            possible += expectation.getCurrentPossibleExpectations()
            if expectation.nbRequiredCalls() > 0:
                break
        return possible

class UnorderedOrderingPolicy:
    def getCurrentPossibleExpectations( self, expectations ):
        possible = []
        for expectation in expectations:
            possible += expectation.getCurrentPossibleExpectations()
        return possible

class AllCompletionPolicy:
    def nbRequiredCalls( self, expectations ):
        required = 0
        for expectation in expectations:
            required += expectation.nbRequiredCalls()
        return required

    def acceptsMoreCalls( self, expectations ):
        return any( len(expectation.getCurrentPossibleExpectations() ) != 0 for expectation in expectations )

    def markExpectationCalled( self, expectations, expectation ):
        pass

class AnyCompletionPolicy:
    def nbRequiredCalls( self, expectations ):
        return 0

    def acceptsMoreCalls( self, expectations ):
        return True

    def markExpectationCalled( self, expectations, expectation ):
        pass

class ExactlyOneCompletionPolicy:
    def nbRequiredCalls( self, expectations ):
        required = 1
        for expectation in expectations:
            if len( expectation.getCurrentPossibleExpectations() ) == 0:
                required = 0
        return required

    def acceptsMoreCalls( self, expectations ):
        return self.nbRequiredCalls( expectations ) == 1

    def markExpectationCalled( self, expectations, expectation ):
        pass

class RepeatedCompletionPolicy:
    def nbRequiredCalls( self, expectations ):
        required = 0
        if expectations[ 0 ].called:
            for expectation in expectations:
                required += expectation.nbRequiredCalls()
        return required

    def acceptsMoreCalls( self, expectations ):
        return True

    def markExpectationCalled( self, expectations, expectation ):
        if expectation is expectations[ -1 ]:
            for e in expectations:
                e.resetCall()

class UnstickyStickynessPolicy:
    def sticky( self ):
        return False

class StickyStickynessPolicy:
    def sticky( self ):
        return True

class ExpectationWrapper( object ):
    def __init__( self, expectation ):
        self.__expectation = expectation
        self.__parent = None
        self.__called = False

    @property
    def name( self ):
        return self.__expectation.name

    def expectsCall( self ):
        return self.__expectation.expectsCall()

    def checkCall( self, args, kwds ):
        return self.__expectation.checkCall( args, kwds )

    def checkName( self, name ):
        return self.__expectation.checkName( name )

    def setParent( self, parent ):
        assert( self.__parent is None )
        self.__parent = parent

    def getCurrentPossibleExpectations( self ):
        if self.__called:
            return []
        else:
            return [ self ]

    def nbRequiredCalls( self ):
        if self.__called:
            return 0
        else:
            return 1

    @property
    def called( self ):
        return self.__called

    def call( self ):
        self.__called = True
        self.__parent.markExpectationCalled( self )
        return self.__expectation.call(), self.__parent.rewindGroups()

    def resetCall( self ):
        self.__called = False

class ExpectationGroup:
    def __init__( self, ordering, completion, stickyness ):
        self.__ordering = ordering
        self.__completion = completion
        self.__stickyness = stickyness
        self.__parent = None
        self.__expectations = []

    def setParent( self, parent ):
        assert( self.__parent is None )
        self.__parent = parent

    @property
    def parent( self ):
        assert( self.__parent is not None )
        return self.__parent

    def addExpectation( self, expectation ):
        wrapper = ExpectationWrapper( expectation )
        wrapper.setParent( self )
        self.__expectations.append( wrapper )

    def addGroup( self, group ):
        group.setParent( self )
        self.__expectations.append( group )

    def getCurrentPossibleExpectations( self ):
        if self.__completion.acceptsMoreCalls( self.__expectations ):
            return self.__ordering.getCurrentPossibleExpectations( self.__expectations )
        else:
            return []

    def nbRequiredCalls( self ):
        return self.__completion.nbRequiredCalls( self.__expectations )

    def getRequiredCallsExamples( self ):
        ### @todo Implement
        return [ "myMock.foobar" ]

    def rewindGroups( self ):
        if self.__shallStick():
            return self
        else:
            return self.__parent.rewindGroups()

    def __shallStick( self ):
        if self.__parent is None:
            return True
        if self.__stickyness.sticky():
            return len( self.getCurrentPossibleExpectations() ) != 0
        return False

    def markExpectationCalled( self, expectation ):
        self.__completion.markExpectationCalled( self.__expectations, expectation )

    def resetCall( self ):
        for e in self.__expectations:
            e.resetCall()

def makeGroup( ordering, completion, stickyness ):
    class Group( ExpectationGroup ):
        def __init__( self ):
            ExpectationGroup.__init__( self, ordering(), completion(), stickyness() )

    return Group

OrderedExpectationGroup = makeGroup( OrderedOrderingPolicy, AllCompletionPolicy, UnstickyStickynessPolicy )
UnorderedExpectationGroup = makeGroup( UnorderedOrderingPolicy, AllCompletionPolicy, UnstickyStickynessPolicy )
AtomicExpectationGroup = makeGroup( OrderedOrderingPolicy, AllCompletionPolicy, StickyStickynessPolicy )
OptionalExpectationGroup = makeGroup( OrderedOrderingPolicy, AnyCompletionPolicy, UnstickyStickynessPolicy )
AlternativeExpectationGroup = makeGroup( UnorderedOrderingPolicy, ExactlyOneCompletionPolicy, UnstickyStickynessPolicy )
RepeatedExpectationGroup = makeGroup( OrderedOrderingPolicy, RepeatedCompletionPolicy, UnstickyStickynessPolicy )
