from Products.Five.browser import BrowserView
from iwwb.eventlist.config import SERVICE_BASE_URL
from urllib2 import HTTPError

import logging
import socket
import urllib
import urllib2

logger = logging.getLogger('iwwb.eventlist')


class ProxyView(BrowserView):
    """
    Pass a AJAX call to a remote server. This view is mainly indended
    to be used with jQuery.load() and jQuery.getJSON() requests.

    This will work around problems when a browser does not support
    Allow-Access-Origin HTTP header (IE).

    Asssuming only HTTP GET requests are made.

    See: http://opensourcehacker.com/2011/08/02/ajax-proxy-view-with-python-urllib-and-plone/
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """
        Use HTTP GET ``url`` query parameter for the target of the real
        request.
        """
        charset = self.request.get("remoteCharset", None)
        enc_info = "" if (not charset) else ";charset={0}".format(charset)

        # Make sure any theming layer won't think this is HTML
        # http://stackoverflow.com/questions/477816/the-right-json-content-type
        self.request.response.setHeader(
            "Content-type",
            "application/json{0}".format(enc_info)
        )

        url = self.request.get("url", None)
        if not url:
            self.request.response.setStatus(500, "url parameter missing")

        if not self.is_allowed(url):
            # The server understood the request, but is refusing to fulfill
            # it. Authorization will not help and the request SHOULD NOT be
            # repeated
            self.request.response.setStatus(
                403, "proxying to the target URL not allowed")
            return

        # Pass other HTTP GET query parameters directly to the target server
        exclude_params = ('url', 'remoteCharset')
        params = {}
        for key, value in self.request.form.items():
            if key not in exclude_params:
                params[key] = value

        # http://www.voidspace.org.uk/python/articles/urllib2.shtml
        data = urllib.urlencode(params)

        full_url = data and (url + "?" + data) or url
        req = urllib2.Request(full_url)

        try:
            # Important if the remote server is slow
            # all our web server threads get stuck here
            # But this is UGLY as Python does not provide per-thread
            # or per-socket timeouts thru urllib
            orignal_timeout = socket.getdefaulttimeout()
            try:
                socket.setdefaulttimeout(10)
                response = urllib2.urlopen(req)
            finally:
                # restore orignal timeoout
                socket.setdefaulttimeout(orignal_timeout)

            # XXX: How to stream response through Zope
            # AFAIK - we cannot do it currently
            return response.read()
        except HTTPError, e:
            # Have something more useful to log output as plain urllib
            # exception using Python logging interface
            # http://docs.python.org/library/logging.html
            logger.error("Server did not return HTTP 200 when calling "
                         "remote proxy URL:" + url)
            for key, value in params.items():
                logger.error(key + ": " + value)

            # Print the server-side stack trace / error page
            logger.error(e.read())

            raise e

    def is_allowed(self, url):
        """
        Check whether we are allowed to call the target URL.

        This prevents using your service as an malicious proxy
        (to call any internet service).
        """
        allowed_prefix = SERVICE_BASE_URL

        if url.startswith(allowed_prefix):
            return True

        return False
