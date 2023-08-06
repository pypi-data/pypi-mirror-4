redturtle.monkey
================

.. image:: https://travis-ci.org/RedTurtle/redturtle.monkey.png?branch=master
   :target: https://travis-ci.org/RedTurtle/redturtle.monkey

Another MailChimp integration for Plone. We did have a reason to not use `collective.mailchimp <https://pypi.python.org/pypi/collective.mailchimp/1.2.1>`_ nor `collective.chimpfeed <https://pypi.python.org/pypi/collective.chimpfeed/1.9.8>`_ (although we have reused/shared some of the concepts you can find there). Simply our use case is different (call it much simpler :)

Use case
--------
Let say you want to configurate MailChimp campaign in Plone (including Plone content of course) and **manually** decide when to push it to chimp cloud service. This is what the *redturtle.monkey* actually do.
You can:

- create multiple campaign configurations
- each configuration:

  - can contain different MailChimp API Keys (or you can use global ones)
  - contain different Plone items to be used as campaign content
  - can have a MailChimp template and subscribers list

Sections/Slots
--------------
What makes *redturtle.monkey* flexible is the ability to register custom `MailChimp template sections <http://kb.mailchimp.com/article/getting-started-with-mailchimps-template-language>`_ (slots) and decide how to render them.
A section is subscriber adapter that you can register with ZCML like that::

  <subscriber provides="redturtle.monkey.interfaces.IMailchimpSlot"
              factory=".generic.Body" />

Then the factory is simple::

 from redturtle.monkey.slots import Slot

 class Body(Slot):
    name = u'body'

The name will be used later by MailChimp so it should correspondent to your *mc:edit* tag.

Last thing is to register content renderer for your new slot::

 <adapter for="* *" factory=".generic.BodyRenderer" name="body"/>

but if you would like to render let say events differently you can do it::

  <adapter for="Products.ATContentTypes.interfaces.IATEvent *"
           factory=".event.BodyRenderer" name="body"/>

It will then look like that::

  from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
  from redturtle.monkey.slots import SlotRenderer

  class BodyRenderer(SlotRenderer):
      template = ViewPageTemplateFile("generic_body.pt")

