from postmonkey import PostMonkey
from postmonkey import MailChimpException
from postmonkey.exceptions import PostRequestError
from plone.registry.interfaces import IRegistry
from zope.interface import implements
from zope.component import getUtility

from redturtle.monkey.interfaces import IMonkeyLocator
from redturtle.monkey.interfaces import IMonkeySettings


def connect(func):
    def wrap_connect(self, *args, **kwargs):
        campaign = kwargs.get('campaign')
        if campaign and getattr(campaign,'api_key', False):
            self.settings = campaign
        else:
            registry = getUtility(IRegistry)
            self.settings = registry.forInterface(IMonkeySettings)
        self.mailchimp = PostMonkey(self.settings.api_key)
        return func(self, *args, **kwargs)
    return wrap_connect


class MonkeyLocator(object):
    """Utility for MailChimp API calls.
    """
    implements(IMonkeyLocator)

    @connect
    def ping(self, campaign=None):
        """Return simple ping to check if the API is correct"""
        return self.mailchimp.ping()

    @connect
    def lists(self, campaign=None):
        """Return all available MailChimp lists.
        http://apidocs.mailchimp.com/api/rtfm/lists.func.php
        """
        #print("MAILCHIMP LOCATOR: lists")
        try:
            # lists returns a dict with 'total' and 'data'. we just need data
            return self.mailchimp.lists()['data']
        except MailChimpException:
            return []
        except PostRequestError:
            return []
        except:
            raise

    @connect
    def templates(self, campaign=None):
        """Return all available MailChimp templates.
        http://apidocs.mailchimp.com/api/rtfm/templates.func.php
        """
        try:
            return self.mailchimp.templates()['user']
        except MailChimpException:
            return []
        except PostRequestError:
            return []
        except:
            raise

    @connect
    def account(self, campaign=None):
        return self.mailchimp.getAccountDetails()

    @connect
    def createCampaign(self, title, subject, list_id, template_id, content, campaign=None):
        options = {'subject': subject,
                   'list_id': list_id,
                   'template_id': template_id,
                   'title': title,
                   'from_email': self.settings.from_email,
                   'from_name': self.settings.from_name}
        try:
            cid = self.mailchimp.campaignCreate(type='regular', options=options, content=content)
            campaign = self.mailchimp.campaigns(filters={'campaign_id':cid})
            return campaign['data'][0]['web_id']
        except MailChimpException:
            raise
        except PostRequestError:
            return None
        except:
            raise

    @connect
    def subscribe(self, list_id, email_address, merge_vars, email_type):
        if not email_type:
            email_type = u'html'
        try:
            self.mailchimp.listSubscribe(
                id=list_id,
                email_address=email_address,
                merge_vars=merge_vars,
                email_type=email_type,
                double_optin=True,
                update_existing=False,
                replace_interests=True,
                send_welcome=False
            )
        except MailChimpException:
            raise
