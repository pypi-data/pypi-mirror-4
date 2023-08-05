import unittest
from zope.testing import doctest

from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import ptc

from Products.Five import zcml, fiveconfigure

import p4a.video

class Layer(ptc.PloneTestCase.layer):

    @classmethod
    def setUp(cls):
        fiveconfigure.debug_mode = True
        zcml.load_config('test.zcml', p4a.video)
        fiveconfigure.debug_mode = False

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        pass

    @classmethod
    def testTearDown(cls):
        pass
    

ptc.setupPloneSite()

def test_suite():
    suite = ztc.ZopeDocFileSuite(
        '../dimensions.txt',
        '../mimetypes.txt',
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE,
        test_class=ptc.PloneTestCase)
    suite.layer = Layer
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
