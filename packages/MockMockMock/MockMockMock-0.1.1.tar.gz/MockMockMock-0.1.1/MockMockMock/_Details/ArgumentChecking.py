class Equality:
    def __init__( self, args, kwds ):
        self.__args = args
        self.__kwds = kwds

    def __call__( self, args, kwds ):
        return self.__args == args and self.__kwds == kwds
