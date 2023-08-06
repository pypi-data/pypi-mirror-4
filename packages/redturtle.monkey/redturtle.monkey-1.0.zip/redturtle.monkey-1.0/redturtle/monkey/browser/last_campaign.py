# -*- coding: utf-8 -*-
from zope.annotation.interfaces import IAnnotations
from Products.CMFPlone.i18nl10n import ulocalized_time
from Products.Five.browser import BrowserView
from redturtle.monkey.content.campaign import LAST_CAMPAIGN


class LastCampaign(BrowserView):
    """ This renders the link to last mailchimp campaign """

    def __call__(self):
        ann = IAnnotations(self.context)

        last_campaign = ann.get(LAST_CAMPAIGN)
        if not last_campaign:
            return None

        date = last_campaign['date']
        if not date:
            return None

        last_campaign['date'] = ulocalized_time(date,
                                                long_format=True,
                                                context=self.context)
        return last_campaign
