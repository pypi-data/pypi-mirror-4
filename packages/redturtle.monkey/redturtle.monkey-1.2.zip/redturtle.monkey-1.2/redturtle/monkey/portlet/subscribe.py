from Acquisition import aq_inner
from zope.interface import alsoProvides
from z3c.form.interfaces import IFormLayer
from plone.z3cform.interfaces import IWrappedForm
from plone.z3cform import z2
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.interface import implements
from zope import schema

from z3c.form import field

from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from z3cformhelpers import AddForm
from z3cformhelpers import EditForm

from redturtle.monkey import  _
from redturtle.monkey.interfaces import INewsletterSubscribe
from redturtle.monkey.browser.newsletter import NewsletterSubscriberForm


class IMailChimpPortlet(IPortletDataProvider):

    name = schema.TextLine(
        title=_(u'Title'),
        description=_(u'Title of the portlet'))

    list_id = schema.Choice(
        title=_(u'Available lists'),
        description=_(u'Select list to subscribe to.'),
        required=True,
        vocabulary='redturtle.monkey.vocabularies.AllCampaignLists'
        )

    custom_css = schema.TextLine(
        title=_(u'Custom css'),
        required=False,
        description=_(u'Custom css class for portlet wrapper'))

    text = schema.Text(
        title=_(u"Text"),
        description=_(u"The text to render"),
        required=False)


class Assignment(base.Assignment):
    implements(IMailChimpPortlet)

    def __init__(self, name=u'', list_id=u'', custom_css=u'', text=u''):
        self.name = name
        self.list_id = list_id
        self.custom_css = custom_css
        self.text = text

    @property
    def title(self):
        return _(u"MailChimp")


class Renderer(base.Renderer):
    fields = field.Fields(INewsletterSubscribe)
    _template = ViewPageTemplateFile('subscribe.pt')
    form = NewsletterSubscriberForm

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    def render(self):
        return xhtml_compress(self._template())

    @property
    def custom_css(self):
        return self.data.custom_css or ''

    @property
    def name(self):
        return self.data.name or _(u"Subscribe to newsletter")

    def text(self):
        return self.data.text or u''

    def update(self):
        super(Renderer, self).update()
        z2.switch_on(self, request_layer=IFormLayer)
        self.form = self.form(aq_inner(self.context), self.request)
        self.form.portlet = self.data
        alsoProvides(self.form, IWrappedForm)
        self.form.update()


class AddForm(AddForm):
    fields = field.Fields(IMailChimpPortlet)
    fields['text'].widgetFactory = WysiwygFieldWidget
    label = _(u"Add MailChimp Portlet")
    description = _(
        u"This portlet displays a subscription form for a " +
        u"MailChimp newsletter.")

    def create(self, data):
        return Assignment(**data)


class EditForm(EditForm):
    fields = field.Fields(IMailChimpPortlet)
    fields['text'].widgetFactory = WysiwygFieldWidget
    label = _(u"Edit MailChimp Portlet")
    description = _(
        u"This portlet displays a subscription form for a " +
        u"MailChimp newsletter.")
