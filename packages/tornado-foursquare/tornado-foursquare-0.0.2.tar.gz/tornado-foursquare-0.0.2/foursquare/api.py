import urllib
from tornado import gen
from tornado.httpclient import HTTPRequest, AsyncHTTPClient

try:
    import json
except ImportError:
    import simplejson as json

FOURSQUARE_URL = "https://api.foursquare.com/v2"
FOURSQUARE_VERSION = "20121019"

class FoursquareError(ValueError):
    
    def __init__(self, meta):
        self.error_type = meta.get('errorType')
        self.code = meta.get('code')
        self.error_detail = meta.get('errorDetail')

        super(FoursquareError, self).__init__(self.error_detail)

class Venues(object):

    def __init__(self, foursquare):
        self.foursquare = foursquare

    @gen.engine
    def get(self, venue_id, callback):
        response = yield gen.Task(self.foursquare._make_request, path='/venues/{}'.format(venue_id))
        callback(response.get('response').get('venue'))

    @gen.engine
    def search(self, callback, **kw):
        response = yield gen.Task(self.foursquare._make_request, path='/venues/search', query=kw)
        callback(response.get('response').get('venues'))

class Foursquare(object):
    
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.venues = Venues(self)

    @gen.engine
    def _make_request(self, path, query=None, method="GET", body=None,
                callback=None):
        """
        Makes request on `path` in the graph.

        path -- endpoint to the foursquare api
        query -- A dictionary that becomes a query string to be appended to the path
        method -- GET, POST, etc
        body -- message body
        callback -- function to be called when the async request finishes
        """
        if not query:
            query = {}

        query['client_id'] = self.client_id
        query['client_secret'] = self.client_secret
        query['v'] = FOURSQUARE_VERSION

        query_string = urllib.urlencode(query) if query else ""
        body = urllib.urlencode(body) if body else None

        url = FOURSQUARE_URL + path
        if query_string:
            url += "?" + query_string

        client = AsyncHTTPClient()
        request = HTTPRequest(url, method=method, body=body)
        response = yield gen.Task(client.fetch, request)
        
        data = json.loads(response.body)
        if data.get('meta').get('code') != 200:
            raise(FoursquareError(data.get('meta')))

        callback(data)
