import re

from postmonkey import PostMonkey

from zope import schema
from zope.interface import Interface
from zope.interface import invariant
from zope.interface import Invalid

from redturtle.monkey import _


class IRedturtleMonkey(Interface):
    """Marker interface that defines a ZTK browser layer. We can reference
    this in the 'layer' attribute of ZCML <browser:* /> directives to ensure
    the relevant registration only takes effect when this theme is installed.

    The browser layer is installed via the browserlayer.xml GenericSetup
    import step.
    """


class IMonkeyLocator(Interface):
    """Interface for mailchimp locator."""


class ICampaign(Interface):
    """Marker interface for AT Campaign."""


class NotAnEmailAddress(schema.ValidationError):
    __doc__ = _(u"Invalid email address")


check_email = re.compile(r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+.)*[a-zA-Z]{2,4}")\
    .match


def validate_email(value):
    if not check_email(value):
        raise NotAnEmailAddress(value)
    return True


class INewsletterSubscribe(Interface):

    email = schema.TextLine(
        title=_(u"Email address"),
        description=_(u"help_email",
                      default=u"Please enter your email address."),
        required=True,
        constraint=validate_email)

    email_type = schema.Choice(
        title=_(u"Mail format"),
        vocabulary="redturtle.monkey.vocabularies.EmailType",
        description=_(u"help_email_type",
                      default=u"Please choose type of newsletter you wish to receive."),
        default="text",
        required=False,
    )

    list_id = schema.TextLine(
        title=_(u"List ID"),
        required=True
    )


class IMonkeySettings(Interface):
    """Global mailchimp settings. This describes records stored in the
    configuration registry and obtainable via plone.registry.
    """

    api_key = schema.TextLine(
        title=_(u"MailChimp API Key"),
        description=_(
            u"help_api_key",
            default=u"Enter in your MailChimp key here (.e.g. " +
                    u"'8b785dcabe4b5aa24ef84201ea7dcded-us4'). Log into " +
                    u"mailchimp.com, go to account -> extras -> API Keys & " +
                    u"Authorized Apps and copy the API Key to this field."
        ),
        default=u"",
        required=True
    )

    from_email = schema.TextLine(
        title=_(u"Email from address"),
        description=_(u"help_from_email",
                      default=u"Please enter FROM email address."),
        required=True,
        constraint=validate_email)

    from_name = schema.TextLine(
        title=_(u"Email from name"),
        description=_(u"help_from_name",
                      default=u"Please enter FROM email name."),
        required=True)

    @invariant
    def valid_api_key(data):
        if len(data.api_key) == 0:
            return
        mailchimp = PostMonkey(data.api_key)
        try:
            return mailchimp.ping()
        except:
            raise Invalid(
                u"Your MailChimp API key is not valid. Please go " +
                u"to mailchimp.com and check your API key.")


class IMailchimpSlot(Interface):
    """A mapping between mailchimp slot and Plone content rendering."""

    name = schema.TextLine(
        title=_(u"Mailchimp slot name"),
        required=True)

    def render(objs=None, **kw):
        """Calls IMailchimpSlotRenderer to generate HTML for slot"""


class IMailchimpSlotRenderer(Interface):
    """Returns the rendered HTML for this slot"""

    def render():
        """Returns the rendered HTML for this slot"""
