from zope.component import getUtility, queryMultiAdapter
from zope.component import subscribers
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

from redturtle.monkey.interfaces import IMonkeyLocator, IMailchimpSlot, IMailchimpSlotRenderer


def available_lists(context):
    mailchimp = getUtility(IMonkeyLocator)
    lists = mailchimp.lists(campaign=context)
    if not lists:
        return SimpleVocabulary([])
    return SimpleVocabulary([
        SimpleTerm(value=li['id'], title=li['name']) for li in lists]
    )


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
