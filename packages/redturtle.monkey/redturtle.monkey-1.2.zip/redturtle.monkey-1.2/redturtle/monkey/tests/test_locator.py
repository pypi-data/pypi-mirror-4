# -*- coding: utf-8 -*-
import unittest2 as unittest

from zope.component import getUtility
from plone.app.testing import TEST_USER_ID, setRoles

from redturtle.monkey.testing import \
    REDTURTLE_MONKEY_INTEGRATION_TESTING


class MonkeyLocatorIntegrationTest(unittest.TestCase):

    layer = REDTURTLE_MONKEY_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()

    def test_mailchimp_locator_registration(self):
        from redturtle.monkey.interfaces import IMonkeyLocator
        self.assertTrue(getUtility(IMonkeyLocator))

    def test_mailchimp_locator_lists_method(self):
        from redturtle.monkey.locator import MonkeyLocator
        locator = MonkeyLocator()
        self.assertTrue(locator.lists())
        self.assertEqual(len(locator.lists()), 2)

    def test_mailchimp_locator_template_method(self):
        from redturtle.monkey.locator import MonkeyLocator
        locator = MonkeyLocator()
        self.assertTrue(locator.templates())
        self.assertEqual(len(locator.templates()), 2)

    def test_mailchimp_locator_create_campaign(self):
        from redturtle.monkey.locator import MonkeyLocator
        locator = MonkeyLocator()
        web_id = locator.createCampaign('Title','Subject','List_id',
                                        'Template_id','The content')
        self.assertEqual(web_id, '123QWE456')

    def test_mailchimp_locator_connect(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory(type_name='Campaign', id='c1')
        self.campaign = self.portal['c1']
        setRoles(self.portal, TEST_USER_ID, ['Member'])

        from redturtle.monkey.locator import MonkeyLocator
        locator = MonkeyLocator()
        locator.ping(campaign=self.campaign)
        self.assertFalse(locator.settings==self.campaign)

        # with proper api_key the settings are set
        self.campaign.setCampaign_api_key('abc')
        locator.ping(campaign=self.campaign)
        self.assertTrue(locator.settings==self.campaign)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
