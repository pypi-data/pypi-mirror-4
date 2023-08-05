# -*- coding: utf-8 -*-
"""Module for communicating with the IWWB web service."""

from iwwb.eventlist.interfaces import IIWWBSearcher
from suds.client import Client
from zope.interface import implements

import logging

logger = logging.getLogger('iwwb.eventlist')

WSDL_URL = 'http://www.iwwb.de/wss/sucheIWWBServer.php?wsdl'

# Set maximum results to a low number, otherwise the search takes too long
RESULTS_PER_PAGE = 1000
MAX_RESULTS = 1000


class IWWBSearcher(object):
    """Utility for fetching results from the IWWWB service."""
    implements(IIWWBSearcher)

    def __init__(self):
        self.client = self._get_service_client()
        self.max_results = MAX_RESULTS
        self.results_per_page = RESULTS_PER_PAGE

    def _get_service_client(self):
        """Return the service client object for accessing the IWWB service.

        :returns: Service client object
        :rtype: suds.client.Client
        """
        try:
            client = Client(WSDL_URL)
            if not isinstance(client, Client):
                raise
        except:
            # Many things can go wrong
            message = "Can't access the IWWB service."
            logger.exception(message)
            raise Exception(message)
        return client

    def get_results(self, query, page=1):
        """Return results from the IWWB service.

        :param query: Dictionary with search parameters and values. For a list
            of possible parameters see:
            http://www.iwwb.de/wss/sucheIWWBServer.php?op=GetFullResult
        :type query: Dictionary
        :param page: Results page to fetch, defaults to 1. If self.max_results
            equals self.results_per_page, we fetch all results at once.
        :type page: int
        :returns: List of search results
        :rtype: SearchResult
        """
        try:
            results_array = self.client.service.GetFullResult(
                maxResult=self.max_results,
                resultPerPage=self.results_per_page,
                page=page,
                **query
            )
        except:
            # Many things can go wrong
            message = "Can't parse IWWB search results."
            logger.exception(message)
            raise Exception(message)

        if not results_array.SearchResults:
            return []

        return [res for res in results_array.SearchResults.SearchResult]
