#!/usr/bin/env python

# Copyright 2012 Vincent Jacques
# vincent@vincent-jacques.net

from distutils.core import setup, Command
import textwrap
import sys
import glob

class test( Command ):
    user_options = []

    def initialize_options( self ):
        pass

    def finalize_options( self ):
        pass

    def run( self ):
        try:
            import coverage
            analyseCoverage = True
        except ImportError:
            print "Unable to import coverage. Running tests without coverage analysis"
            analyseCoverage = False
        if analyseCoverage:
            cov = coverage.coverage(branch=True)
            cov.start()

        import MockMockMock.tests
        ok = MockMockMock.tests.run().wasSuccessful()

        if analyseCoverage:
            cov.stop()
            for f in glob.glob( "MockMockMock/*.py" ):
                ok = ok and len( cov.analysis2( f )[ 3 ] ) == 0
            cov.report(file=sys.stdout, include="MockMockMock/*")
        if ok:
            exit( 0 )
        else:
            exit( 1 )

setup(
    name = "MockMockMock",
    version = "0.1.1",
    description = "My mock library. Don't use it (yet)",
    author = "Vincent Jacques",
    author_email = "vincent@vincent-jacques.net",
    url = "",
    long_description = textwrap.dedent( """\
    """ ),
    packages = [
        "MockMockMock",
        "MockMockMock._Details",
        "MockMockMock.tests",
    ],
    classifiers = [
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development",
    ],
    cmdclass = { "test": test },
)
