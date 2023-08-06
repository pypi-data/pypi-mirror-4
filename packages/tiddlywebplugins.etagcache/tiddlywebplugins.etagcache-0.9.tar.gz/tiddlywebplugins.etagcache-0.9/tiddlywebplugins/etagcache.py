"""
Keep a cache of ETags so we don't need to access the store
to do validation.

This operates as a two tiered piece of middleware.

On the request side it checks if the request is a GET
and if it includes an If-None-Match header. If it does it
looks up the current URI in the cache and compares the value
with what's in the If-Match header. If they are the same
we can raise a 304 right now.

On the response side, if the current request is a GET
and the outgoing response has an ETag, put the current
URI and ETag into the cache.

Store HOOKs are used to invalidate the cache through the
management of namespaces.

Installation is simply adding the plugin name to system_plugins
and twanager_plugins in tiddlywebconfig.py
"""

import logging
import uuid  # for namespacing
import urllib

from httpexceptor import HTTP304, HTTP415

from tiddlyweb.util import sha
from tiddlyweb.web.util import get_serialize_type
from tiddlyweb.web.negotiate import Negotiate
from tiddlywebplugins.caching import (container_namespace_key,
        ANY_NAMESPACE, BAGS_NAMESPACE, RECIPES_NAMESPACE)


LOGGER = logging.getLogger(__name__)


class EtagCache(object):
    """
    Middleware that manages a cache of uri:etag pairs. The
    request half of the app checks the cache and raises 304
    on matches. The response half stores data in the cache.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        LOGGER.debug('%s entering', __name__)
        try:
            _mc = environ['tiddlyweb.store'].storage.mc
        except AttributeError:
            _mc = None
        if _mc:
            self._mc = _mc
            LOGGER.debug('%s checking cache', __name__)
            self._check_cache(environ, start_response)

            def replacement_start_response(status, headers, exc_info=None):
                """
                Record status and headers for later manipulation.
                """
                self.status = status
                self.headers = headers
                return start_response(status, headers, exc_info)

            output = self.application(environ, replacement_start_response)

            LOGGER.debug('%s checking response', __name__)
            self._check_response(environ)

            return output
        else:
            return self.application(environ, start_response)

    def _check_cache(self, environ, start_response):
        """
        Look in the cache for a match on the current request. That
        request much be a GET and include an If-None-Match header.

        If there is a match, send an immediate 304.
        """
        if environ['REQUEST_METHOD'] == 'GET':
            uri = _get_uri(environ)
            LOGGER.debug('%s with %s %s', __name__, uri,
                    environ['REQUEST_METHOD'])
            if _cacheable(environ, uri):
                match = environ.get('HTTP_IF_NONE_MATCH', None)
                if match:
                    LOGGER.debug('%s has match %s', __name__, match)
                    cached_etag = self._mc.get(self._make_key(environ, uri))
                    LOGGER.debug('%s comparing cached %s to %s', __name__,
                            cached_etag, match)
                    if cached_etag and cached_etag == match:
                        LOGGER.debug('%s cache hit for %s', __name__, uri)
                        raise HTTP304(match)
                    else:
                        LOGGER.debug('%s cache miss for %s', __name__, uri)
                else:
                    LOGGER.debug('%s no if none match for %s', __name__, uri)

    def _check_response(self, environ):
        """
        If the current response is in response to a GET then attempt
        to cache it.
        """
        if environ['REQUEST_METHOD'] == 'GET':
            uri = _get_uri(environ)
            if _cacheable(environ, uri):
                for name, value in self.headers:
                    if name.lower() == 'etag':
                        self._cache(environ, value)

    def _cache(self, environ, value):
        """
        Add the uri and etag to the cache.
        """
        uri = _get_uri(environ)
        LOGGER.debug('%s adding to cache %s:%s', __name__, uri, value)
        self._mc.set(self._make_key(environ, uri), value)

    def _make_key(self, environ, uri):
        """
        Build a key for the current request. The key is a combination
        of the current namespace, the current content type, the current
        user, the host, and the uri.
        """
        try:
            mime_type = get_serialize_type(environ)[1]
            mime_type = mime_type.split(';', 1)[0].strip()
        except (TypeError, AttributeError, HTTP415):
            config = environ['tiddlyweb.config']
            default_serializer = config['default_serializer']
            serializers = config['serializers']
            mime_type = serializers[default_serializer][1]
        LOGGER.debug('%s mime_type %s for %s', __name__, mime_type, uri)
        username = environ['tiddlyweb.usersign']['name']
        namespace = self._get_namespace(environ, uri)
        host = environ.get('HTTP_HOST', '')
        uri = uri.decode('UTF-8', 'replace')
        key = '%s:%s:%s:%s:%s' % (namespace, mime_type, username, host, uri)
        return sha(key.encode('UTF-8')).hexdigest()

    def _get_namespace(self, environ, uri):
        """
        Calculate the namespace in which we will look for a match.

        The namespace is built from the current URI.
        """
        prefix = environ.get('tiddlyweb.config', {}).get('server_prefix', '')

        index = 0
        if prefix:
            index = 1

        uri_parts = uri.split('/')[index:]

        if '/bags/' in uri:
            container = uri_parts[1]
            bag_name = uri_parts[2]
            key = container_namespace_key(container, bag_name)
        elif '/recipes/' in uri:
            if '/tiddlers' in uri:
                key = container_namespace_key(ANY_NAMESPACE)
            else:
                container = uri_parts[1]
                recipe_name = uri_parts[2]
                key = container_namespace_key(container, recipe_name)
        # bags or recipes
        elif '/bags' in uri:
            key = container_namespace_key(BAGS_NAMESPACE)
        elif '/recipes' in uri:
            key = container_namespace_key(RECIPES_NAMESPACE)
        # anything that didn't already match, like friendly uris or
        # search
        else:
            key = container_namespace_key(ANY_NAMESPACE)

        namespace = self._mc.get(key)
        if not namespace:
            namespace = '%s' % uuid.uuid4()
            LOGGER.debug('%s no namespace for %s, setting to %s', __name__,
                    key, namespace)
            self._mc.set(key.encode('utf8'), namespace)

        LOGGER.debug('%s current namespace %s:%s', __name__,
                key, namespace)

        return namespace


def _cacheable(environ, uri):
    """
    Is the current uri cacheable?
    For the time being attempt to cache anything.
    """
    return True


def _get_uri(environ):
    """
    Reconstruct the current uri from the environment.
    """
    uri = urllib.quote(environ.get('SCRIPT_NAME', '')
            + environ.get('PATH_INFO', ''))
    if environ.get('QUERY_STRING'):
        uri += '?' + environ['QUERY_STRING']
    return uri


def init(config):
    """
    Initialize and configure the plugin. If selector, we are on
    the web server side and need to adjust filters. The rest is
    for both system and twanager plugins: hooks used to invalidate
    the cache.
    """
    if 'selector' in config:
        if EtagCache not in config['server_request_filters']:
            config['server_request_filters'].insert(
                    config['server_request_filters'].index(Negotiate) + 1,
                    EtagCache)
