import unittest
import collections

import MockMockMock
import MockMockMock._Details.ArgumentChecking

def isCallable( x ):
    return isinstance( x, collections.Callable )

class TestException( Exception ):
    pass

class PublicInterface( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mocks = MockMockMock.Engine()
        self.myMock = self.mocks.create( "myMock" )

    def testMockMockMock( self ):
        self.assertEqual( self.dir( MockMockMock ), [ "Engine", "Exception", "tests" ] )

    def testEngine( self ):
        self.assertEqual( self.dir( self.mocks ), [ "alternative", "atomic", "create", "optional", "ordered", "repeated", "tearDown", "unordered" ] )
        self.assertFalse( isCallable( self.mocks ) )

    def testMock( self ):
        self.assertEqual( self.dir( self.myMock ), [ "expect", "object" ] )
        self.assertFalse( isCallable( self.myMock ) )

    def testExpect( self ):
        self.assertEqual( self.dir( self.myMock.expect ), [] )
        self.assertTrue( isCallable( self.myMock.expect ) )

    def testExpectation( self ):
        self.assertEqual( self.dir( self.myMock.expect.foobar ), [ "andExecute", "andRaise", "andReturn", "withArguments" ] )
        self.assertTrue( isCallable( self.myMock.expect.foobar ) )

    def testCalledExpectation( self ):
        self.assertEqual( self.dir( self.myMock.expect.foobar( 42 ) ), [ "andExecute", "andRaise", "andReturn" ] )
        self.assertFalse( isCallable( self.myMock.expect.foobar( 42 ) ) )
        self.assertEqual( self.dir( self.myMock.expect.foobar.withArguments( 42 ) ), [ "andExecute", "andRaise", "andReturn" ] )
        self.assertFalse( isCallable( self.myMock.expect.foobar.withArguments( 42 ) ) )

    def testCalledThenAndedExpectation( self ):
        self.assertEqual( self.dir( self.myMock.expect.foobar( 42 ).andReturn( 12 ) ), [] )
        self.assertFalse( isCallable( self.myMock.expect.foobar( 42 ).andReturn( 12 ) ) )
        self.assertEqual( self.dir( self.myMock.expect.foobar( 42 ).andRaise( TestException() ) ), [] )
        self.assertFalse( isCallable( self.myMock.expect.foobar( 42 ).andRaise( TestException() ) ) )
        self.assertEqual( self.dir( self.myMock.expect.foobar( 42 ).andExecute( lambda : 12 ) ), [] )
        self.assertFalse( isCallable( self.myMock.expect.foobar( 42 ).andExecute( lambda : 12 ) ) )

    def testAndedExpectation( self ):
        self.assertEqual( self.dir( self.myMock.expect.foobar.andReturn( 12 ) ), [] )
        self.assertFalse( isCallable( self.myMock.expect.foobar.andReturn( 12 ) ) )
        self.assertEqual( self.dir( self.myMock.expect.foobar.andRaise( TestException() ) ), [] )
        self.assertFalse( isCallable( self.myMock.expect.foobar.andRaise( TestException() ) ) )
        self.assertEqual( self.dir( self.myMock.expect.foobar.andExecute( lambda : 12 ) ), [] )
        self.assertFalse( isCallable( self.myMock.expect.foobar.andExecute( lambda : 12 ) ) )

    def testObject( self ):
        ### @todo Maybe expose expected calls in myMock.object.__dir__
        self.assertEqual( self.dir( self.myMock.object ), [] )

    def dir( self, o ):
        return sorted( a for a in dir( o ) if not a.startswith( "_" ) )

class SingleExpectation( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mocks = MockMockMock.Engine()
        self.myMock = self.mocks.create( "myMock" )

    def tearDown( self ):
        self.mocks.tearDown()

    def testMethodCall( self ):
        self.myMock.expect.foobar()
        self.myMock.object.foobar()

    def testMethodCallWithSimpleArgument( self ):
        self.myMock.expect.foobar( 42 )
        self.myMock.object.foobar( 42 )

    def testMethodCallWithReturn( self ):
        returnValue = object()
        self.myMock.expect.foobar().andReturn( returnValue )
        # Not only "==" but "is"
        self.assertTrue( self.myMock.object.foobar() is returnValue )

    def testPropertyWithReturn( self ):
        self.myMock.expect.foobar.andReturn( 42 )
        self.assertEqual( self.myMock.object.foobar, 42 )

    def testObjectCallWithArgumentsAndReturn( self ):
        self.myMock.expect( 43, 44 ).andReturn( 42 )
        self.assertEqual( self.myMock.object( 43, 44 ), 42 )

    def testMethodCallWithRaise( self ):
        self.myMock.expect.foobar().andRaise( TestException() )
        with self.assertRaises( TestException ):
            self.myMock.object.foobar()

    def testPropertyWithRaise( self ):
        self.myMock.expect.foobar.andRaise( TestException() )
        with self.assertRaises( TestException ):
            self.myMock.object.foobar

    def testMethodCallWithSpecificAction( self ):
        self.check = False
        def f():
            self.check = True
        self.myMock.expect.foobar().andExecute( f )
        self.myMock.object.foobar()
        self.assertTrue( self.check )

    def testPropertyWithSpecificAction( self ):
        self.check = False
        def f():
            self.check = True
        self.myMock.expect.foobar.andExecute( f )
        self.myMock.object.foobar
        self.assertTrue( self.check )

class SingleExpectationNotCalled( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mocks = MockMockMock.Engine()
        self.myMock = self.mocks.create( "myMock" )

    def testMethodCallWithBadArgument( self ):
        self.myMock.expect.foobar( 42 )
        with self.assertRaises( MockMockMock.Exception ) as cm:
            self.myMock.object.foobar( 43 )
        self.assertEqual( cm.exception.message, "myMock.foobar called with bad arguments" )

    def testMethodCallWithBadName( self ):
        self.myMock.expect.foobar()
        with self.assertRaises( MockMockMock.Exception ) as cm:
            self.myMock.object.barbaz()
        self.assertEqual( cm.exception.message, "myMock.barbaz called instead of myMock.foobar" )

    def testMethodCallWithBadName2( self ):
        self.myMock.expect.foobar2()
        with self.assertRaises( MockMockMock.Exception ) as cm:
            self.myMock.object.barbaz()
        self.assertEqual( cm.exception.message, "myMock.barbaz called instead of myMock.foobar2" )

    def testPropertyWithBadName( self ):
        self.myMock.expect.foobar.andReturn( 42 )
        with self.assertRaises( MockMockMock.Exception ) as cm:
            self.myMock.object.barbaz
        self.assertEqual( cm.exception.message, "myMock.barbaz called instead of myMock.foobar" )

    def testMethodNotCalled( self ):
        self.myMock.expect.foobar()
        with self.assertRaises( MockMockMock.Exception ) as cm:
            self.mocks.tearDown()
        self.assertEqual( cm.exception.message, "myMock.foobar not called" )
        self.myMock.object.foobar()
        self.mocks.tearDown()

    def testPropertyNotCalled( self ):
        self.myMock.expect.foobar
        with self.assertRaises( MockMockMock.Exception ) as cm:
            self.mocks.tearDown()
        self.assertEqual( cm.exception.message, "myMock.foobar not called" )
        self.myMock.object.foobar
        self.mocks.tearDown()

class ExpectationSequence( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mocks = MockMockMock.Engine()
        self.myMock = self.mocks.create( "myMock" )

    def testTwoCalls( self ):
        self.myMock.expect.foobar()
        self.myMock.expect.barbaz()
        self.myMock.object.foobar()
        self.myMock.object.barbaz()
        self.mocks.tearDown()

    def testCallNotExpectedFirst( self ):
        self.myMock.expect.foobar()
        self.myMock.expect.barbaz()
        with self.assertRaises( MockMockMock.Exception ) as cm:
            self.myMock.object.barbaz()
        self.assertEqual( cm.exception.message, "myMock.barbaz called instead of myMock.foobar" )

    def testCallWithArgumentsNotExpectedFirst( self ):
        self.myMock.expect.foobar( 42 )
        self.myMock.expect.foobar( 43 )
        with self.assertRaises( MockMockMock.Exception ) as cm:
            self.myMock.object.foobar( 43 )
        self.assertEqual( cm.exception.message, "myMock.foobar called with bad arguments" )

    def testManyCalls( self ):
        self.myMock.expect.foobar( 1 )
        self.myMock.expect.foobar( 2 )
        self.myMock.expect.foobar( 3 )
        self.myMock.expect.foobar( 4 )
        self.myMock.expect.foobar( 5 )
        self.myMock.expect.foobar( 6 )
        self.myMock.object.foobar( 1 )
        self.myMock.object.foobar( 2 )
        self.myMock.object.foobar( 3 )
        self.myMock.object.foobar( 4 )
        self.myMock.object.foobar( 5 )
        self.myMock.object.foobar( 6 )
        self.mocks.tearDown()

class SequenceBetweenSeveralLinkedMocks( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mocks = MockMockMock.Engine()
        self.m1 = self.mocks.create( "m1" )
        self.m2 = self.mocks.create( "m2" )

    def testShortCorrectSequence( self ):
        self.m1.expect.foobar( 42 )
        self.m2.expect.foobar( 43 )
        self.m1.object.foobar( 42 )
        self.m2.object.foobar( 43 )
        self.mocks.tearDown()

    def testShortInvertedSequence( self ):
        self.m1.expect.foobar( 42 )
        self.m2.expect.foobar( 43 )
        with self.assertRaises( MockMockMock.Exception ) as cm:
            self.m2.object.foobar( 43 )
        self.assertEqual( cm.exception.message, "m2.foobar called instead of m1.foobar" )

class SequenceBetweenSeveralIndependentMocks( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mocks1 = MockMockMock.Engine()
        self.mocks2 = MockMockMock.Engine()
        self.m1 = self.mocks1.create( "m1" )
        self.m2 = self.mocks2.create( "m2" )

    def testSameOrderSequence( self ):
        self.m1.expect.foobar( 42 )
        self.m2.expect.foobar( 43 )
        self.m1.object.foobar( 42 )
        self.m2.object.foobar( 43 )
        self.mocks1.tearDown()
        self.mocks2.tearDown()

    def testOtherOrderSequence( self ):
        self.m1.expect.foobar( 42 )
        self.m2.expect.foobar( 43 )
        self.m2.object.foobar( 43 )
        self.m1.object.foobar( 42 )
        self.mocks1.tearDown()
        self.mocks2.tearDown()

class ArgumentCheckers( unittest.TestCase ):
    def testCheckerIsUsedByCall( self ):
        # We use a myMock...
        checker = MockMockMock.Engine().create( "checker" )
        checker.expect( ( 12, ), {} ).andReturn( True )
        checker.expect( ( 13, ), {} ).andReturn( False )
    
        # ...to test a mock!
        m = MockMockMock.Engine().create( "m" )
        m.expect.foobar.withArguments( checker.object ).andReturn( 42 )
        m.expect.foobar.withArguments( checker.object ).andReturn( 43 )
        self.assertEqual( m.object.foobar( 12 ), 42 )
        with self.assertRaises( MockMockMock.Exception ) as cm:
            m.object.foobar( 13 )
        self.assertEqual( cm.exception.message, "m.foobar called with bad arguments" )

    # def testIdentityChecker( self ):
    # def testTypeChecker( self ):
    # def testRangeChecker( self ):

    def testEqualityChecker( self ):
        c = MockMockMock._Details.ArgumentChecking.Equality( ( 1, 2, 3 ), { 1: 1, 2: 2, 3: 3 } )
        self.assertTrue( c( ( 1, 2, 3 ), { 1: 1, 2: 2, 3: 3 } ) )
        self.assertFalse( c( ( 1, 2, 3 ), { 1: 1, 2: 2, 3: 4 } ) )
        self.assertFalse( c( ( 1, 2, 4 ), { 1: 1, 2: 2, 3: 3 } ) )

class Ordering( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mocks = MockMockMock.Engine()
        self.myMock = self.mocks.create( "myMock" )

    def testUnorderedGroupOfSameMethod( self ):
        with self.mocks.unordered:
            self.myMock.expect.foobar( 1 ).andReturn( 11 )
            self.myMock.expect.foobar( 1 ).andReturn( 13 )
            self.myMock.expect.foobar( 2 ).andReturn( 12 )
            self.myMock.expect.foobar( 1 ).andReturn( 14 )
        self.assertEqual( self.myMock.object.foobar( 2 ), 12 )
        self.assertEqual( self.myMock.object.foobar( 1 ), 11 )
        self.assertEqual( self.myMock.object.foobar( 1 ), 13 )
        self.assertEqual( self.myMock.object.foobar( 1 ), 14 )
        self.mocks.tearDown()

    ### @todo Allow unordered property and method calls on the same name: difficult
    def testUnorderedGroupOfSameMethodAndProperty( self ):
        with self.assertRaises( MockMockMock.Exception ) as cm:
            with self.mocks.unordered:
                self.myMock.expect.foobar()
                self.myMock.expect.foobar
            self.myMock.object.foobar
        self.assertEqual( cm.exception.message, "myMock.foobar is expected as a property and as a method call in an unordered group" )

    def testUnorderedGroupOfSamePropertyAndMethod( self ):
        with self.assertRaises( MockMockMock.Exception ) as cm:
            with self.mocks.unordered:
                self.myMock.expect.foobar
                self.myMock.expect.foobar()
            self.myMock.object.foobar()
        self.assertEqual( cm.exception.message, "myMock.foobar is expected as a property and as a method call in an unordered group" )
