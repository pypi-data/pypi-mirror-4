from zExceptions import Redirect
from persistent.dict import PersistentDict
from postmonkey import MailChimpException
from zope.component import getUtility
from zope.component import subscribers
from zope.annotation.interfaces import IAnnotations
from zope.schema.interfaces import IVocabularyFactory
from Products.ATContentTypes.interfaces import IATTopic
from Products.CMFCore.utils import getToolByName
try:
    from plone.app.collection.interfaces import ICollection
    from plone.app.contentlisting.interfaces import IContentListingObject
    COLLECTION = True
except ImportError:
    COLLECTION = False
from plone.app.uuid.utils import uuidToObject
from plone.uuid.interfaces import IUUID
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser import BrowserView
from DateTime import DateTime

from redturtle.monkey.content.campaign import LAST_CAMPAIGN
from redturtle.monkey.interfaces import IMonkeyLocator, IMailchimpSlot
from redturtle.monkey import  _


class AddItems(BrowserView):

    def __call__(self):
        """ Process the relation for campaign items. """
        redirect_url = self.context.absolute_url()
        items = self.request.form.get('items',[])
        if not items:
            IStatusMessage(self.request).add(_(u'We have problems processing '
                              'your request. Not items found.'), type='error')
            return self.request.RESPONSE.redirect(redirect_url)

        my_uid = IUUID(self.context)

        for item in items:
            campaign = uuidToObject(item['uid'])
            existing_relations = campaign.getRawCampaign_items()
            if item.get('enabled',False):
                if my_uid not in existing_relations:
                    IStatusMessage(self.request).add(_(u'Item added to campaign.'))
                    existing_relations.append(my_uid)
            else:
                if my_uid in existing_relations:
                    IStatusMessage(self.request).add(_(u'Item removed from campaign.'))
                    existing_relations.remove(my_uid)
            campaign.setCampaign_items(existing_relations)

        return self.request.RESPONSE.redirect(redirect_url)


class CampaignWizard(BrowserView):

    def __call__(self):
        """Redirect POST requests to generateCampaign."""
        if self.request.method == 'POST':
            return self.generateCampaign()
        else:
            return super(CampaignWizard, self).__call__()

    def available(self):
        mailchimp = getUtility(IMonkeyLocator)
        try:
            mailchimp.ping(campaign=self.context)
        except:
            return False
        if not self.context.getCampaign_items():
            return False
        return True

    def list_templates(self):
        """List all available mailchimp templates."""
        vfactory = getUtility(IVocabularyFactory,
                      name='redturtle.monkey.vocabularies.AvailableTemplates')
        return vfactory(self.context)

    def list_clists(self):
        """List all available mailchimp lists."""
        vfactory = getUtility(IVocabularyFactory,
                      name='redturtle.monkey.vocabularies.AvailableLists')
        return vfactory(self.context)

    def list_slots(self):
        """List all avaible IMailchimpSlot subscribers for given context."""
        vfactory = getUtility(IVocabularyFactory,
                      name='redturtle.monkey.vocabularies.AvailableSlots')
        return vfactory(self.context)

    def list_campaign_items(self):
        """List all campaign items group by folderish/nonfolderish types."""
        items = self.context.getCampaign_items()
        result = {u'manual_items':[]}
        wft = getToolByName(self.context, 'portal_workflow')
        def walk(items, result, parent):
            for item in items:
                collection = []
                if COLLECTION and IContentListingObject.providedBy(item):
                    item = item.getObject()
                elif IATTopic.providedBy(item):
                    collection = item.queryCatalog(b_size=100, full_objects=True)
                elif COLLECTION and ICollection.providedBy(item):
                    collection = item.getQuery()

                if collection:
                    result[item.title_or_id()] = []
                    walk(collection, result, item.title_or_id())
                else:
                    # add only published items
                    if wft.getInfoFor(item, "review_state") != "published":
                        IStatusMessage(self.request).\
                        add(_(u'Some of the items in your list are private. '
                               'They were not included in the wizard - '
                               'MailChimp supports only published content.'),
                            type='error')
                        continue

                    result[parent].append({'uid': IUUID(item),
                                           'title': item.title_or_id()})
            return result

        result = walk(items, result, u'manual_items')
        return result

    def addLastCampaign(self, campaign_id, title):
        if campaign_id:
            if not title:
                title = _(u'Unknown campaign title')
            ann = IAnnotations(self.context)
            ann[LAST_CAMPAIGN] = PersistentDict()
            ann[LAST_CAMPAIGN]['id'] = campaign_id
            ann[LAST_CAMPAIGN]['title'] = title
            ann[LAST_CAMPAIGN]['date'] = DateTime()

    def generateCampaign(self):
        """By calling mailchimp API creates a campaign and redirects
        user to the proper URL."""
        mailchimp = getUtility(IMonkeyLocator)
        form = self.request.form
        subject = form.get('campaign_title')
        list_id = form.get('list')
        template_id = form.get('template')
        description = form.get('campaign_description')
        title = form.get('campaign_title')

        content = self.generateCampaignContent(objs=form.get('items'), **form)
        if not content:
            IStatusMessage(self.request).add(_(u'Couldn\'t generate campaign items.'))
            raise Redirect,\
                self.request.response.redirect('%s/campaign_wizard' % \
                                                  self.context.absolute_url())
        try:
            campaign_id = mailchimp.createCampaign(subject=subject,
                                          list_id=list_id,
                                          title='%s %s' % (title, description),
                                          content=content,
                                          template_id=template_id,
                                          campaign=self.context)
            self.addLastCampaign(campaign_id, title)
            IStatusMessage(self.request).add(_(u'Mailchimp campaign created.'))
            return self.request.response.redirect(
                                 '%s/@@campaign_created?id=%s' % \
                                 (self.context.absolute_url(), campaign_id))
        except MailChimpException, e:
            IStatusMessage(self.request).add(e, type='error')
            raise Redirect,\
                self.request.response.redirect(self.context.absolute_url())

    def generateCampaignContent(self, objs=None, **kw):
        """Tries to render the html content for the campaign items,
        using the slot subscribers."""
        content = {}
        if not objs:
            return content

        items_in_slots = {}
        for item in objs:
            if not item.get('enabled'):
                continue
            if item['slot'] not in items_in_slots:
                items_in_slots[item['slot']] = []
            items_in_slots[item['slot']].append(uuidToObject(item['uid']))

        slots = subscribers([self.context], IMailchimpSlot)
        for slot in slots:
            objs = items_in_slots.get(slot.name, [])
            html = slot.render(objs=objs, **kw)
            if not html: # Let's skip empty slots
                continue
            content['html_%s' % slot.name] = html
        return content
