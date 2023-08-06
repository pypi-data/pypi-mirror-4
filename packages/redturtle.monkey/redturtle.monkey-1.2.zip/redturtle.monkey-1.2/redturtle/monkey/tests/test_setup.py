import unittest2 as unittest

from redturtle.monkey.testing import \
    REDTURTLE_MONKEY_INTEGRATION_TESTING


class TestSetup(unittest.TestCase):

    layer = REDTURTLE_MONKEY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_browserlayer_available(self):
        from plone.browserlayer import utils
        from redturtle.monkey.interfaces import IRedturtleMonkey
        self.failUnless(IRedturtleMonkey in utils.registered_layers())


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
