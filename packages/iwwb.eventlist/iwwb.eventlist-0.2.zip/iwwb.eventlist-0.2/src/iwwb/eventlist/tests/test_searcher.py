# -*- coding: utf-8 -*-
"""Tests for the IWWB Searcher utility."""

from iwwb.eventlist.tests.base import IntegrationTestCase
from iwwb.eventlist.interfaces import IIWWBSearcher
from zope.component import getUtility

import mock
import unittest2 as unittest


class TestIWWBSearcherMocked(unittest.TestCase):
    """Unit test on IWWBSearcher using mocked service results."""

    @mock.patch('iwwb.eventlist.searcher.Client')
    def test_catch_exception_on_invalid_client(self, suds_client):
        """Test an exception is caugth if suds.client.Client() returns one when
        trying to access an invalid SOAP client.
        """
        from iwwb.eventlist.searcher import IWWBSearcher

        suds_client.return_value = None
        suds_client.side_effect = Exception('Invalid SUDS client')

        with self.assertRaises(Exception):
            IWWBSearcher()._get_service_client()

    @mock.patch('iwwb.eventlist.searcher.IWWBSearcher._get_service_client')
    def test_return_empty_list_for_empty_results(self, _get_service_client):
        """An empty list must be returned if we get empty SearchResults."""
        from iwwb.eventlist.searcher import IWWBSearcher

        # IWWB service returns '' if it doesn't find any results
        _get_service_client.return_value.service.GetFullResult.return_value.SearchResults = ''

        self.assertEquals(IWWBSearcher().get_results(dict(query='foo')), [])


class TestIWWBSearcherIntegration(IntegrationTestCase):
    """Integration test for the IWWBSearcher utility that actually call the
    service and assert results.
    """

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.searcher = getUtility(IIWWBSearcher)
        self.searcher.results_per_page = 2

    def test_get_results_empty(self):
        # Search for events in a city that doesn't exist
        query = dict(city='FooBar')
        self.assertEquals(self.searcher.get_results(query), [])

    def test_get_results_not_empty(self):
        # This search should return some results
        query = dict(city='Berlin')
        self.assertGreater(len(self.searcher.get_results(query)), 0)

    def test_get_results_format(self):
        query = dict(city='Berlin')
        results = self.searcher.get_results(query)
        result = results[0]

        # See if we can access the attribute values for a result (we can't test
        # other attributes because they are not mandatory), this should not
        # throw an Attribute error.
        result.Rank
        result.Type

    def test_get_results_false_parameters(self):
        # Try searching with a nonexistent parameter, the method should fail
        query = dict(foo='bar')
        try:
            self.searcher.get_results(query)
        except:
            pass
        else:
            self.fail("get_results did not raise an Exception!")


def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above."""
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
