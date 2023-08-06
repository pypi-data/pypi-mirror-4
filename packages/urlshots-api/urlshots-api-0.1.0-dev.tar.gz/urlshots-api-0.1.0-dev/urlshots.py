"""
"""
import logging

import urllib3
import pyconfig
from pytool.lang import hashed_singleton, Namespace, UNSET


__version__ = '0.1.0-dev'


@hashed_singleton
class API(object):
    """
    This is the UrlShots API client.

    :param int delay: Delay in seconds after loading before screenshotting
                      (default: ``0``)
    :param int jpeg: JPEG compression; 0 means no JPEG, return a PNG instead
                     (default: ``75``)
    :param int compress: Whether to compress a PNG to an 8-bit indexed image
                         (defalt: ``0``)
    :param int timeout: Timeout when hitting the API (default: ``20``)
    :param str actions: Actions chain as a string (default: ``None``)
    :param str concurrency: Maximum connection pool size for use in
                            multithreaded or concurrent applications
                            (default: ``1``)
    :param tuple window: Size of the capture window to use as a tuple of
                         ``(width, height)`` (default: ``(1260, 840)``)
    :param str host: UrlShots API hostname (default: ``'urlshots.net'``)

    """

    # Default options
    opts = Namespace()
    opts.delay = 0
    opts.jpeg = 75
    opts.compress = 0
    opts.timeout = 20
    opts.actions = UNSET
    opts.concurrency = 1
    opts.window = (1260, 840)
    opts.host = 'urlshots.net'
    # This converts the opts to pyconfig settings
    for name, value in opts:
        setattr(opts, name, pyconfig.setting('urlshots.' + name, value))
    del name, value # Remove left over vars so they don't end up in the class

    def __init__(self, **kwargs):
        # Parse keyword options
        for name, value in self.opts:
            if name in kwargs:
                setattr(self.opts, name, kwargs.pop(name))
        # This is our thread safe connection pool, thanks urllib3!
        self.http = urllib3.HTTPConnectionPool(self.opts.host,
                timeout=self.opts.timeout, maxsize=self.opts.concurrency)
        self.log = logging.getLogger('urlshots')
        # Debug the options in case folks want to know
        self.log.debug("Options:")
        for name, value in self.opts:
            self.log.debug("  %s = %r", name, value)

    def _params(self):
        """ Return the instance options as a set of params for the API. """
        params = self.opts.as_dict()
        # Remove the options that are not for the API
        for name in 'concurrency', 'timeout', 'host':
            params.pop(name)
        # Remove actions if it's not set
        if params['actions'] is UNSET:
            params.pop('actions')
        # Coerce window size
        params['window'] = '{}x{}'.format(*params['window'])
        return params

    def request(self, url, params=None):
        """ Return a response object for `url`.

            :param str url: URL to capture
            :param dict params: Override parameters sent to API (optional)

        """
        # Get arguments to the API
        params = params or self._params()
        params['url'] = url
        # Make the request
        return self.http.request('GET', '/render', params)

    def image(self, url):
        """ Return a binary image of `url`.

            :param str url: URL to capture

        """
        response = self.request(url)
        if response.status != 200:
            return None
        return response.data

