from zope.component import getUtility, queryMultiAdapter
from zope.component import subscribers
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from Products.CMFCore.utils import getToolByName

from redturtle.monkey.interfaces import IMonkeyLocator, IMailchimpSlot, IMailchimpSlotRenderer


def available_lists(context):
    mailchimp = getUtility(IMonkeyLocator)
    lists = mailchimp.lists(campaign=context)
    if not lists:
        return SimpleVocabulary([])
    return SimpleVocabulary([
        SimpleTerm(value=li['id'], title=li['name']) for li in lists]
    )

def all_campaign_lists(context):
    mailchimp = getUtility(IMonkeyLocator)
    result = {}

    # first for current context
    lists = mailchimp.lists(campaign=context)
    for li in lists:
        result[li['id']] = SimpleTerm(value=li['id'],
                                      title=li['name'])

    # next for all campaigns
    portal_catalog = getToolByName(context, 'portal_catalog')
    brains = portal_catalog(portal_type='Campaign')
    for brain in brains:
        campaign = brain.getObject()
        if not campaign:
            continue
        lists = mailchimp.lists(campaign=campaign)
        for li in lists:
            result[li['id']] = SimpleTerm(value=li['id'],
                                          title='%s - %s' % (campaign.title_or_id(),
                                                             li['name']))
    return SimpleVocabulary(result.values())


def available_templates(context):
    mailchimp = getUtility(IMonkeyLocator)
    templates = mailchimp.templates(campaign=context)
    if not templates:
        return SimpleVocabulary([])
    return SimpleVocabulary([
        SimpleTerm(value=str(li['id']), title=li['name']) for li in templates]
    )


def available_slots(context):
    slots = subscribers([context], IMailchimpSlot)
    return SimpleVocabulary([
        SimpleTerm(value=str(li.name), title=li.name) for li in slots \
                if queryMultiAdapter((context, context.REQUEST),
                                     IMailchimpSlotRenderer, name=li.name)]
    )


def email_type(context):
    terms = []
    terms.append(
        SimpleTerm(
            value='text',
            token='text',
            title='Plain text',
        )
    )
    terms.append(
        SimpleTerm(
            value='html',
            token='html',
            title='HTML',
        )
    )
    return SimpleVocabulary(terms)
