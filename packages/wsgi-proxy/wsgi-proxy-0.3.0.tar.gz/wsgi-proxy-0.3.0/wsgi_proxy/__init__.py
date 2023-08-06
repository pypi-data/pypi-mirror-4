""":mod:`wsgi_proxy` --- Python package of :program:`wsgi-proxy`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is an importable Python package that consists of basic WSGI app
and other frontends around it.  The most important thing for you is
probably :data:`app` and its type :class:`WSGIProxyApplication`.

You can use this with other third-party WSGI servers.  For example:

.. sourcecode:: console

   $ pip install gunicorn
   $ gunicorn -p8080 wsgi_proxy:app

"""
import httplib
import logging
import urlparse


#: (:class:`frozenset`) The set of hop-by-hop headers.  All header names
#: all normalized to lowercase.
HOPPISH_HEADERS = frozenset([
    'connection', 'keep-alive', 'proxy-authenticate',
    'proxy-authorization', 'te', 'trailers', 'transfer-encoding',
    'upgrade', 'proxy-connection'
])


def is_hop_by_hop(header):
    """Returns :const:`True` if the given ``header`` is hop by hop.

    :param header: the header name
    :type header: :class:`basestring`
    :returns: whether the given ``header`` is hop by hop or not
    :rtype: :class:`bool`

    """
    return header.lower() in HOPPISH_HEADERS


def reconstruct_url(environ):
    """Reconstruct the remote url from the given WSGI ``environ`` dictionary.

    :param environ: the WSGI environment
    :type environ: :class:`collections.MutableMapping`
    :returns: the remote url to proxy
    :rtype: :class:`basestring`

    """
    # From WSGI spec, PEP 333
    url = environ.get('PATH_INFO', '')
    # Fix ;arg=value in url
    if '%3B' in url:
        url, arg = url.split('%3B', 1)
        url = ';'.join([url, arg.replace('%3D', '=')])
    # Stick query string back in
    try:
        query_string = environ['QUERY_STRING']
    except KeyError:
        pass
    else:
        url += '?' + query_string
    environ['reconstructed_url'] = url
    return url


class WSGIProxyApplication(object):
    """WSGI application to handle requests that need to be proxied.
    You have to instantiate the class before using it as WSGI app::

        from wsgiref.simple_server import make_server

        app = WSGIProxyApplication()
        make_server('', 8080, app).serve_forever()

    """

    #: (:class:`types.ClassType`) The connection class of :mod:`httplib` module.
    #: It should be a subtype of :class:`httplib.HTTPConnection`.
    #: Default is :class:`httplib.HTTPConnection`.
    connection_class = httplib.HTTPConnection

    def handler(self, environ, start_response):
        """Proxy for requests to the actual http server"""
        logger = logging.getLogger(__name__ + '.WSGIProxyApplication.handler')
        url = urlparse.urlparse(reconstruct_url(environ))

        # Create connection object
        try:
            connection = self.connection_class(url.netloc)
            # Build path
            path = url.geturl().replace('%s://%s' % (url.scheme, url.netloc),
                                        '')
        except Exception:
            start_response('501 Gateway Error', [('Content-Type', 'text/html')])
            logger.exception('Could not Connect')
            yield '<H1>Could not connect</H1>'
            return

        # Read in request body if it exists
        body = None
        try:
            length = int(environ['CONTENT_LENGTH'])
        except (KeyError, ValueError):
            pass
        else:
            body = environ['wsgi.input'].read(length)

        # Build headers
        logger.debug('environ = %r', environ)
        headers = dict(
            (key, value)
            for key, value in (
                # This is a hacky way of getting the header names right
                (key[5:].lower().replace('_', '-'), value)
                for key, value in environ.items()
                # Keys that start with HTTP_ are all headers
                if key.startswith('HTTP_')
            )
            if not is_hop_by_hop(key)
        )

        # Handler headers that aren't HTTP_ in environ
        try:
            headers['content-type'] = environ['CONTENT_TYPE']
        except KeyError:
            pass

        # Add our host if one isn't defined
        if 'host' not in headers:
            headers['host'] = environ['SERVER_NAME']

        # Make the remote request
        try:
            logger.debug('%s %s %r',
                         environ['REQUEST_METHOD'], path, headers)
            connection.request(environ['REQUEST_METHOD'], path,
                               body=body, headers=headers)
        except Exception as e:
            # We need extra exception handling in the case the server fails
            # in mid connection, it's an edge case but I've seen it
            start_response('501 Gateway Error', [('Content-Type', 'text/html')])
            logger.exception(e)
            yield '<H1>Could not connect</H1>'
            return

        response = connection.getresponse()

        hopped_headers = response.getheaders()
        headers = [(key, value)
                   for key, value in hopped_headers
                   if not is_hop_by_hop(key)]

        start_response('{0.status} {0.reason}'.format(response), headers)
        while True:
            chunk = response.read(4096)
            if chunk:
                yield chunk
            else:
                break

    def __call__(self, environ, start_response):
        return self.handler(environ, start_response)


#: (:class:`WSGIProxyApplication`) The builtin instance of
#: :class:`WSGIProxyApplication`.  In the most cases what all you need
#: is only this.
app = WSGIProxyApplication()
