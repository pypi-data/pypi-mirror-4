import unittest2 as unittest
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from redturtle.monkey.testing import \
    REDTURTLE_MONKEY_INTEGRATION_TESTING


class TestMonkeyVocabularies(unittest.TestCase):

    layer = REDTURTLE_MONKEY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_template_vocabs(self):
        vfactory = getUtility(IVocabularyFactory,
                      name='redturtle.monkey.vocabularies.AvailableTemplates')
        vocab = vfactory(self.portal)
        self.assertTrue(u'My template' in [a.title for a in vocab])

    def test_list_vocabs(self):
        vfactory = getUtility(IVocabularyFactory,
                      name='redturtle.monkey.vocabularies.AvailableLists')
        vocab = vfactory(self.portal)
        self.assertTrue(u'ACME Newsletter' in [a.title for a in vocab])

    def test_slots_vocabs(self):
        vfactory = getUtility(IVocabularyFactory,
                      name='redturtle.monkey.vocabularies.AvailableSlots')
        vocab = vfactory(self.portal)
        self.assertTrue(u'main_primopiano' in [a.title for a in vocab])
