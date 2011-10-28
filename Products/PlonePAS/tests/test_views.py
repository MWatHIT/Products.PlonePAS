# -*- encoding: utf-8 -*-

from DateTime import DateTime
from OFS.Image import Image

from Products.PloneTestCase.ptc import default_user

from Products.PlonePAS.tests import base
from Products.PlonePAS.tests import dummy


class TestPASSearchView(base.TestCase):
    
    def test_sort(self):
        pas_search = self.portal.restrictedTraverse('@@pas_search')
        values = [{'title': u'Sociologie'}, {'title': u'Économie'},
                  {'title': u'anthropologie'}]
        sorted_values = pas_search.sort(values, 'title')
        self.assertEqual(sorted_values,
                         [{'title': 'anthropologie'}, {'title': 'Économie'},
                          {'title': 'Sociologie'}])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPASSearchView))
    return suite
