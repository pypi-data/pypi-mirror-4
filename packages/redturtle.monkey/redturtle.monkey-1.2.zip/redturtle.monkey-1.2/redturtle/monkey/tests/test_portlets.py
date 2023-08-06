import unittest2 as unittest

from zope.component import getUtility, getMultiAdapter
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletManager
from plone.app.testing import TEST_USER_ID, setRoles
from plone.uuid.interfaces import IUUID

from redturtle.monkey.testing import \
    REDTURTLE_MONKEY_INTEGRATION_TESTING
from redturtle.monkey.portlet.addtocampaign import Assignment


class TestMonkeyPortlet(unittest.TestCase):

    layer = REDTURTLE_MONKEY_INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer['request']
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory(type_name='Folder', id='f1')
        self.folder = self.portal['f1']
        self.folder.invokeFactory(type_name='Campaign', id='c1')
        self.campaign = self.folder['c1']

    def test_list_campaigns(self):
        context = self.folder
        request = self.request
        view = self.portal.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = Assignment()
        renderer = getMultiAdapter((context, request, view, manager, assignment),
                                   IPortletRenderer)
        self.assertTrue(self.campaign in renderer.list_campaign()['not_related'])

    def test_add_to_campaign(self):
        self.assertFalse(self.campaign.getRawCampaign_items())

        items = [{'uid': IUUID(self.campaign),
                  'enabled': True}]
        self.request.form['items'] = items
        view = getMultiAdapter((self.folder, self.request), name='add-items-to-campaign')
        self.assertEqual(view(),'http://nohost/plone/f1')
        self.assertEqual(self.campaign.getRawCampaign_items(), [IUUID(self.folder),])





