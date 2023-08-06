import unittest2 as unittest

from zope.component import getMultiAdapter
from plone.app.testing import logout, TEST_USER_ID, setRoles
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName

from redturtle.monkey.testing import \
    REDTURTLE_MONKEY_INTEGRATION_TESTING


class TestMonkeyWizard(unittest.TestCase):

    layer = REDTURTLE_MONKEY_INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer['request']
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.portal_workflow.setChainForPortalTypes(
            ['Event', 'Folder', 'Collection'],
            ['simple_publication_workflow'])
        self.portal.invokeFactory(type_name='Folder', id='f1')
        self.folder = self.portal['f1']
        self.folder.invokeFactory(type_name='Campaign', id='c1')
        self.campaign = self.folder['c1']
        setRoles(self.portal, TEST_USER_ID, ['Member'])

    def test_monkey_wizard_view_vocabularies(self):
        view = getMultiAdapter((self.campaign, self.request),
                               name="campaign_wizard")
        self.assertTrue('ACME Newsletter' in [a.title
                                              for a in view.list_clists()])
        self.assertTrue('My template' in [a.title
                                          for a in view.list_templates()])

    def test_wizard_availability(self):
        view = getMultiAdapter((self.campaign, self.request),
                               name="campaign_wizard")
        # the fresh campaign doesn't have any related items:
        self.assertFalse(self.campaign.getCampaign_items())
        self.assertFalse(view.available())

        # let's add some items
        self.folder.invokeFactory(type_name='Event', id='e1')
        self.folder.e1.setTitle(u'Event 1')
        self.folder.invokeFactory(type_name='Event', id='e2')
        self.folder.e2.setTitle(u'Event 2')
        self.campaign.setCampaign_items([IUUID(self.folder.e1),
                                         IUUID(self.folder.e2)])
        self.assertTrue(view.available())

    def test_monkey_wizard_generate_campaign(self):
        from zExceptions import Redirect

        view = getMultiAdapter((self.campaign, self.request),
                               name="campaign_wizard")

        # without proper form we should be redirected, too:
        try:
            view.generateCampaign()
        except Redirect, e:
            self.assertEqual(e.message, 'http://nohost/plone/f1/c1/campaign_wizard')
        except Exception, e:
            self.fail('Unexpected exception thrown:', e)
        else:
            self.fail('Redirect not thrown')

        # Let's add related items
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.folder.invokeFactory(type_name='Event', id='e1')
        self.folder.e1.setTitle(u'Event 1')
        self.folder.invokeFactory(type_name='Event', id='e2')
        self.folder.e2.setTitle(u'Event 2')
        setRoles(self.portal, TEST_USER_ID, ['Member'])

        self.request.form['campaign_title'] = 'Title'
        self.request.form['list'] = 'List id'
        self.request.form['template'] = 'Template id'
        self.request.form['items'] = [{'slot': 'main_primopiano',
                                       'uid': IUUID(self.folder.e2),
                                       'enabled': True},
                                      {'slot': 'main_body',
                                       'uid': IUUID(self.folder.e1),
                                       'enabled': True}]
        # now we should get a proper Redirect
        self.assertEqual(view.generateCampaign(), 'http://nohost/plone/f1/c1/@@campaign_created?id=123QWE456')

    def test_monkey_wizard_view_protected(self):
        from AccessControl import Unauthorized
        logout()
        self.assertRaises(
            Unauthorized,
            self.campaign.restrictedTraverse,
            '@@campaign_wizard'
        )

    def test_monkey_wizard_content_generation(self):
        view = getMultiAdapter((self.campaign, self.request),
                               name="campaign_wizard")

        # First the campaign is empty
        self.assertEqual(view.generateCampaignContent(objs=[]), {})

        # Let's add related items
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.folder.invokeFactory(type_name='Event', id='e1')
        self.folder.e1.setTitle(u'Event 1')
        self.folder.invokeFactory(type_name='Event', id='e2')
        self.folder.e2.setTitle(u'Event 2')
        setRoles(self.portal, TEST_USER_ID, ['Member'])

        items = [{'slot': 'main_primopiano',
                  'uid': IUUID(self.folder.e2),
                  'enabled': True},
                 {'slot': 'main_body',
                  'uid': IUUID(self.folder.e1),
                  'enabled': True}]

        content = view.generateCampaignContent(objs=items)
        self.assertTrue('html_main_body' in content)
        self.assertTrue('html_main_primopiano' in content)

        # Finally let's check the HTML
        self.assertTrue('<h1>Event 2</h1>' in content['html_main_primopiano'])
        self.assertTrue('<h2>Event 1</h2>' in content['html_main_body'])

    def test_monkey_wizard_list_campaign_items(self):
        wft = getToolByName(self.portal, 'portal_workflow')
        view = getMultiAdapter((self.campaign, self.request),
                               name="campaign_wizard")

        # First the campaign is empty
        self.assertEqual(view.list_campaign_items(), {u'manual_items': []})

        # Let's add related items
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.folder.invokeFactory(type_name='Event', id='e1')
        self.folder.e1.setTitle(u'Event 1')
        self.folder.invokeFactory(type_name='Event', id='e2')
        self.folder.e2.setTitle(u'Event 2')
        self.campaign.setCampaign_items([IUUID(self.folder.e1),
                                         IUUID(self.folder.e2)])
        setRoles(self.portal, TEST_USER_ID, ['Member'])

        # Because the related items are private they shouldn't appear
        # in the campaign items
        self.assertEqual(view.list_campaign_items()['manual_items'], [])

        # Now let's publish one
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        wft.doActionFor(self.folder.e1, "publish")
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.assertEqual(len(view.list_campaign_items()['manual_items']), 1)

        # Finally let's check the topic handling
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.folder.invokeFactory(type_name='Collection', id='collection')
        self.collection = self.folder.collection
        self.collection.setTitle(u'My collection')
        query = [{
            'i': 'Type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Event',
        }]
        self.collection.setQuery(query)
        wft.doActionFor(self.collection, "publish")
        self.campaign.setCampaign_items([IUUID(self.collection),
                                         IUUID(self.folder.e1),
                                         IUUID(self.folder.e2)])
        setRoles(self.portal, TEST_USER_ID, ['Member'])

        # Now we should have those two sections:
        items = view.list_campaign_items()
        self.assertEqual(len(items.keys()), 2)
        self.assertEqual(len(items[u'My collection']), 1)
        self.assertEqual(len(items['manual_items']), 1)
