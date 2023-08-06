# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope.component import getMultiAdapter
from plone.app.portlets.portlets import base
from plone.app.uuid.utils import uuidToObject
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.config import REFERENCE_CATALOG
from zope.interface import implements

from redturtle.monkey import  _


class IAddToCampaign(Interface):
    """
    Interface for Add to campaign
    """


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('addtocampaign.pt')

    @property
    def title(self):
        return _(u"Add item to campaign")

    def list_campaign(self):
        result = {'related': [],
                  'not_related': []}

        reference_catalog = getToolByName(self.context, REFERENCE_CATALOG)
        references = reference_catalog.getBackReferences(self.context,
                                          relationship="campaignItems")
        related = [a.sourceUID for a in references]

        portal_catalog = getToolByName(self.context, 'portal_catalog')
        brains = portal_catalog(portal_type='Campaign')
        not_related = [a.UID for a in brains if a.UID not in related]

        result['related'] = [uuidToObject(u) for u in related]
        result['not_related'] = [uuidToObject(u) for u in not_related]
        return result

    @property
    def available(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        if portal_state.anonymous():
            return False
        else:
            return True


class Assignment(base.Assignment):
    """
    Assignement for Add to campaign
    """
    implements(IAddToCampaign)

    @property
    def title(self):
        return _(u"Office information portlet")


class AddForm(base.NullAddForm):
    """
    AddForm for Add to campaign
    """
    def create(self):
        assignment = Assignment()
        return assignment


class EditForm(base.EditForm):
    """
    EditForm for Add to campaign
    """
