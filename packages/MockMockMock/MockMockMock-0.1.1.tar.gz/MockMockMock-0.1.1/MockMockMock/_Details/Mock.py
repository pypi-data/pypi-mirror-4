class Mock( object ):
    def __init__( self, name, handler ):
        self.__name = name
        self.__handler = handler

    @property
    def expect( self ):
        return self.__handler.expect( self.__name )

    @property
    def object( self ):
        return self.__handler.object( self.__name )
