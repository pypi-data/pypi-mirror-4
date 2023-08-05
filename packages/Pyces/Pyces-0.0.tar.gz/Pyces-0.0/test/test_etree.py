from unittest import TestCase

class SimpleTest( TestCase ):
    def test_hello( self ):
        from pyces import etree
        self.assertEquals( etree.hello( "abc" ), "abc" )
