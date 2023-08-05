class Expectation( object ):
    def __init__( self, name ):
        self.name = name
        self.__checker = None
        self.__action = lambda : None

    # expect
    def expectCall( self, checker ):
        self.__checker = checker

    def setAction( self, action ):
        self.__action = action

    # check
    def checkName( self, name ):
        return self.name == name

    def expectsCall( self ):
        return self.__checker is not None

    def checkCall( self, args, kwds ):
        return self.__checker( args, kwds )

    # call
    def call( self ):
        return self.__action()
