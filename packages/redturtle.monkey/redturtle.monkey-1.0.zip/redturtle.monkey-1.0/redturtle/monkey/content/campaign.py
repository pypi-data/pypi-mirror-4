"""Definition of the Campaign content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.base import ATContentTypeSchema
from Products.ATContentTypes.content import schemata
from archetypes.referencebrowserwidget import ReferenceBrowserWidget

from redturtle.monkey import  _
from redturtle.monkey.config import PROJECTNAME
from redturtle.monkey.interfaces import ICampaign


LAST_CAMPAIGN = 'redturtle.monkey.last_campaign'


CampaignSchema = ATContentTypeSchema.copy() + atapi.Schema((

    atapi.StringField('campaign_api_key',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Campaign API key"),
            description=_(u"Custom Mailchimp API key for this campaign"),
        ),
    ),

    atapi.StringField('campaign_from_email',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Campaign FROM email"),
            description=_(u"Custom Mailchimp FROM email for this campaign"),
        ),
    ),

    atapi.StringField('campaign_from_name',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Campaign FROM name"),
            description=_(u"Custom Mailchimp FROM name for this campaign"),
        ),
    ),

    atapi.ReferenceField('campaign_items',
        relationship = 'campaignItems',
        multiValued = True,
        languageIndependent = False,
        widget = ReferenceBrowserWidget(
            allow_search = True,
            allow_browse = True,
            allow_sorting = True,
            show_indexes = False,
            force_close_on_insert = True,
            show_results_without_query = True,
            label = _(u'label_campaign_items', default=u'Campaign\'s items'),
            description = '',
            visible = {'edit' : 'visible', 'view' : 'invisible' },
            )
        ),

    ))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

CampaignSchema['title'].storage = atapi.AnnotationStorage()
CampaignSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    CampaignSchema,
    folderish=False,
    moveDiscussion=False
)


class Campaign(ATCTContent):
    """Monkey campaign"""
    implements(ICampaign)

    meta_type = "Campaign"
    schema = CampaignSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    @property
    def api_key(self):
        return self.getCampaign_api_key()

    @property
    def from_name(self):
        return self.getCampaign_from_name()

    @property
    def from_email(self):
        return self.getCampaign_from_email()

atapi.registerType(Campaign, PROJECTNAME)
