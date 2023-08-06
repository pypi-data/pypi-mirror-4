from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from redturtle.monkey.slots import Slot, SlotRenderer
from redturtle.monkey import  _


class Header(Slot):
    name = _(u'main_primopiano')

class HeaderRenderer(SlotRenderer):
    template = ViewPageTemplateFile("main-primopiano.pt")


class Body(Slot):
    name = _(u'main_body')

class BodyRenderer(SlotRenderer):
    template = ViewPageTemplateFile("main-body.pt")


class PreHeaderContent(Slot):
    name = _(u'preheader_content')
    template = ViewPageTemplateFile("preheader_content.pt")

    def render(self, objs=None, **kw):
        if kw.get('campaign_description'):
            return self.template(description=kw['campaign_description'])


class CampaignTitle(Slot):
    name = _(u'campaign_title')
    template = ViewPageTemplateFile("campaign-title.pt")

    def render(self, objs=None, **kw):
        if kw.get('campaign_title'):
            return self.template(title=kw['campaign_title'])


class HeaderNumber(Slot):
    name = _(u'header_number')
    template = ViewPageTemplateFile("header-number.pt")

    def render(self, objs=None, **kw):
        if kw.get('campaign_number'):
            return self.template(number=kw['campaign_number'])


class HeaderTitle(Slot):
    name = _(u'header_title')
    template = ViewPageTemplateFile("header-title.pt")

    def render(self, objs=None, **kw):
        if kw.get('campaign_description'):
            return self.template(description=kw['campaign_description'])
