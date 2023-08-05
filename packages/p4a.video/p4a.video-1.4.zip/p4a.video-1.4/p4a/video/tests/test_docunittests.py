import unittest
from zope import component
from zope.component import testing
from zope.testing import doctestunit

def test_suite():
    return unittest.TestSuite((
        doctestunit.DocTestSuite('p4a.video.utils'),
        
        doctestunit.DocFileSuite('media-player.txt',
                                 package="p4a.video",
                                 setUp=testing.setUp,
                                 tearDown=testing.tearDown),

        doctestunit.DocFileSuite('migration.txt',
                                 package="p4a.video",
                                 setUp=testing.setUp,
                                 tearDown=testing.tearDown)
        ))
