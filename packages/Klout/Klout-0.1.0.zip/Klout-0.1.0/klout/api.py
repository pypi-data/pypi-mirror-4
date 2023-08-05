# -*- coding: utf-8 -*-

"""
A minimalist klout API interface. Use of this API 
requires klout *developer key*. You can get registered and
get a key at

    <http://klout.com/s/developers/v2>

====================
Quickstart
====================

Install the PyPi package::
    
    pip install Klout

This short example shows how to get a kloutId first and fetch user's score using that kloutId::

    from klout import *
    
    # Make the Klout object
    k = Klout('YOUR_KEY_HERE')

    # Get kloutId of the user by inputting a twitter screenName
    kloutId = k.identity.klout(screenName="erfaan").get('id')

    # Get klout score of the user
    score = k.user.score(kloutId=kloutId).get('score')

    print "User's klout score is: %s" % (score) 


"""

try:
    import urllib.request as urllib_request
    import urllib.error as urllib_error
    import urllib.parse as urllib_parse
except ImportError:
    import urllib2 as urllib_request
    import urllib2 as urllib_error
    import urllib as urllib_parse

try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

import gzip

try:
    import json
except ImportError:
    import simplejson as json


class _DEFAULT(object):
    pass


class KloutError( Exception ):
    """
    Base Exception thrown by Klout object when there is a
    general error interacting with the API.
    """

    def __init__(self, e):
        self.e = e

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return ( "ERROR: %s" % self.e )


class KloutHTTPError( KloutError ):
    """
    Exception thrown by Klout object when there is an
    HTTP error interacting with api.klout.com.
    """

    def __init__( self, e, uri ):
        self.e = e
        self.uri = uri


class KloutCall( object ):

    def __init__(self, key, domain, 
        callable_cls, api_version = "", 
        uri = "", uriparts = None):
        
        self.key = key
        self.domain = domain
        self.api_version = api_version
        self.callable_cls = callable_cls
        self.uri = uri
        self.uriparts = uriparts

    def __getattr__(self, k):
        try:
            return object.__getattr__(self, k)
        except AttributeError:
            def extend_call(arg):
                return self.callable_cls(
                    key=self.key, domain=self.domain,
                    api_version=self.api_version,
                    callable_cls=self.callable_cls, uriparts=self.uriparts \
                        + (arg,))
            if k == "_":
                return extend_call
            else:
                return extend_call(k)

    def __call__(self, **kwargs):
        # Build the uri.
        uriparts = []
        api_version = self.api_version
        resource = "%s.json" % self.uriparts[0]
        
        uriparts.append(api_version)
        uriparts.append(resource)
        
        params = {}
        if self.key:
            params['key'] = self.key
        
        # append input variables
        for k, v in kwargs.items():
            if k == 'screenName':
                uriparts.append('twitter')
                params[k] = v
            elif k == 'kloutId':
                uriparts.append(str(v))
            else:
                uriparts.append(k)
                uriparts.append(str(v))
        
        for uripart in self.uriparts[1:]:
            if not uripart == 'klout':
                uriparts.append(str(uripart))
        
        uri = '/'.join(uriparts)
        if len(params) > 0:
            uri += '?' + urllib_parse.urlencode(params)
        
        uriBase = "http://%s/%s" % (
            self.domain, uri)
        headers = {'Accept-Encoding': 'gzip'}
        
        req = urllib_request.Request(uriBase, headers=headers)
        
        return self._handle_response(req, uri)
    
    def _handle_response(self, req, uri):
        try:
            handle = urllib_request.urlopen(req)
            if handle.info().get('Content-Encoding') == 'gzip':
                # Handle gzip decompression
                buf = StringIO(handle.read())
                f = gzip.GzipFile(fileobj=buf)
                data = f.read()
            else:
                data = handle.read()
            
            res = json.loads(data.decode('utf8'))
            return res
        except urllib_error.HTTPError as e:
            raise KloutHTTPError( e, uri)


class Klout(KloutCall):
    """
    A minimalist yet fully featured klout API interface. 

    Get RESTful data by accessing members of this class. The result
    is decoded python objects (dicts and lists).

    The klout API is documented at:

        http://klout.com/s/developers/v2

    Examples:

    We need a *developer key* to call any Klout API function

    >>> f = open('key')
    >>> key= f.readline().strip()
    >>> f.close()
    >>> k = Klout(key)
    
    **Identity Resource**
    
    All calls to the Klout API now require a unique kloutId. 
    To facilitate this, you must first translate a {network}/{networkId} into a kloutId.
    
    * Get kloutId by twitter id

    >>> k.identity.klout(tw="11158872")
    {u'id': u'11747', u'network': u'ks'}
    
    * Get kloutId by twitter screenName

    >>> k.identity.klout(screenName="erfaan")
    {u'id': u'11747', u'network': u'ks'}
    
    * Get kloutId by google plus id

    >>> k.identity.klout(gp="112975106809988327760")
    {u'id': u'11747', u'network': u'ks'}
    
    **User Resource**

    Once we have kloutId, we can use this resource to lookup user's score, influcent or topics

    * Get user score

    >>> k.user.score(kloutId='11747') # doctest: +ELLIPSIS
    ...                               # doctest: +NORMALIZE_WHITESPACE
    {u'score': ..., u'scoreDelta': {u'dayChange': ..., u'monthChange': ...}} 

    * Get user influences

    >>> k.user.influence(kloutId='11747') # doctest: +ELLIPSIS
    ...                                   # doctest: +NORMALIZE_WHITESPACE
    {u'myInfluencersCount': ..., u'myInfluenceesCount': ..., \
    u'myInfluencers': [...], u'myInfluencees': [...]}


    * Get user topics

    >>> k.user.topics(kloutId='11747') # doctest: +ELLIPSIS
    ...                                # doctest: +NORMALIZE_WHITESPACE
    [{u'imageUrl': ..., u'slug': ..., u'displayName': ..., u'id': ..., u'name': ...}, ...]

    """

    def __init__(
        self, key, domain="api.klout.com",
        api_version=_DEFAULT):
        """
        """

        if api_version is _DEFAULT:
            api_version = "v2"

        KloutCall.__init__(
            self, key=key, domain = domain, 
            api_version = api_version,
            callable_cls=KloutCall, uriparts=())

__all__ = ["Klout", "KloutError", "KloutHTTPError"]