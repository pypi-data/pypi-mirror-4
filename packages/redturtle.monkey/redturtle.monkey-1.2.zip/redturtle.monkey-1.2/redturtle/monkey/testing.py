import random
import string
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.testing import z2

from redturtle.monkey.interfaces import IMonkeySettings

def id_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return u''.join(random.choice(chars) for x in range(size))


class RedturtleMonkey(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        from mocker import Mocker
        from mocker import ANY
        from mocker import KWARGS
        mocker = Mocker()
        postmonkey = mocker.replace("postmonkey")
        mailchimp = postmonkey.PostMonkey(ANY)
        mocker.count(0, 1000)
        # Lists
        mailchimp.lists()
        mocker.count(0, 1000)
        mocker.result({
            u'total': 2,
            u'data': [{
                    u'id': id_generator(),
                    u'web_id': 625,
                    u'name': u'ACME Newsletter',
                    u'default_from_name': u'info@acme.com',
                },
                {
                    u'id': id_generator(),
                    u'web_id': 626,
                    u'name': u'ACME Newsletter 2',
                    u'default_from_name': u'info@acme.com',
                },
            ]})
        # Ping
        mailchimp.ping()
        mocker.count(0, 1000)
        mocker.result(True)
        # Templates
        mailchimp.templates()
        mocker.count(0, 1000)
        mocker.result({'user':
                      [{ u'id': 1,
                         u'name': u'My template',
                         u'layout': u'basic',
                         u'preview_image': u'http://nohost/preview.jpg',
                         u'date_created': u'2013/01/01',
                         u'edit_source': True,
                       },
                       { u'id': 2,
                         u'name': u'My template 2',
                         u'layout': u'advanced',
                         u'preview_image': u'http://nohost/preview.jpg',
                         u'date_created': u'2012/01/01',
                         u'edit_source': False}
                      ]
        })
        # Campaigns
        mailchimp.campaignCreate(KWARGS)
        mocker.count(0, 1000)
        mocker.result(123)
        mailchimp.campaigns(KWARGS)
        mocker.count(0, 1000)
        mocker.result({'data':[{'web_id': '123QWE456'}]})
        # Get account details
        mailchimp.getAccountDetails()
        mocker.count(0, 1000)
        mocker.result({
            u'total': 1,
            u'data': [{
                u'use_awesomebar': True,
                u'beamer_address': u'NWVmY2ZkYjjNjc=@campaigns.mailchimp.com',
                u'web_id': 17241,
                u'name': u'Test Newsletter',
                u'email_type_option': False,
                u'modules': [],
                u'default_language': u'de',
                u'default_from_name': u'Timo Stollenwerk',
                u'visibility': u'pub',
                u'subscribe_url_long':
                    u'http://johndoe.us4.list-manage1.com/subscribe?u=5e&id=fd',
                u'default_subject': u'Test Newsletter',
                u'subscribe_url_short': u'http://eepurl.com/h6Rjg',
                u'default_from_email': u'no-reply@timostollenwerk.net',
                u'date_created': u'2011-12-27 16:15:03',
                u'list_rating': 0,
                u'id': u'f6257645gs',
                u'stats': {
                    u'grouping_count': 0,
                    u'open_rate': None,
                    u'member_count': 0,
                    u'click_rate': None,
                    u'cleaned_count_since_send': 0,
                    u'member_count_since_send': 0,
                    u'target_sub_rate': None,
                    u'group_count': 0,
                    u'avg_unsub_rate': None,
                    u'merge_var_count': 2,
                    u'unsubscribe_count': 0,
                    u'cleaned_count': 0,
                    u'avg_sub_rate': None,
                    u'unsubscribe_count_since_send': 0,
                    u'campaign_count': 1
                    }
                }
            ]})

        mocker.replay()

        # Load ZCML
        import redturtle.monkey
        self.loadZCML(package=redturtle.monkey)
        z2.installProduct(app, 'redturtle.monkey')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'redturtle.monkey:default')

        registry = getUtility(IRegistry)
        mailchimp_settings = registry.forInterface(IMonkeySettings)
        mailchimp_settings.api_key = u"abc"

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'redturtle.monkey')


REDTURTLE_MONKEY_FIXTURE = RedturtleMonkey()
REDTURTLE_MONKEY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(REDTURTLE_MONKEY_FIXTURE,),
    name="RedturtleMonkey:Integration")
REDTURTLE_MONKEY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(REDTURTLE_MONKEY_FIXTURE,),
    name="RedturtleMonkey:Functional")
