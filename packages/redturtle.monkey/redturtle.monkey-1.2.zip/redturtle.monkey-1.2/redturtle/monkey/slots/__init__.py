from zope.interface import implements, Interface
from zope.component import getMultiAdapter, adapts

from redturtle.monkey.interfaces import IMailchimpSlot, IMailchimpSlotRenderer


class Slot(object):
    implements(IMailchimpSlot)
    adapts(Interface)
    name = u''

    def __init__(self, context):
        self.context = context
        self.request = context.REQUEST

    def render(self, objs=None, **kw):
        result = []
        for obj in objs:
            view = getMultiAdapter((obj, self.request),
                                    IMailchimpSlotRenderer,
                                    name=self.name)
            result.append(view())
        return '\n'.join(result)


class SlotRenderer(object):
    implements(IMailchimpSlotRenderer)
    template = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return self.template()
