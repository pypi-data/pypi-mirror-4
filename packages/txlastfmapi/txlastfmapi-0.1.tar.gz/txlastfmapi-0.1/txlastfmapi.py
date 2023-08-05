import json
import urllib

import lastfmapi
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent
from twisted.web.http_headers import Headers


class JSONDecoder(Protocol):
    '''A body delivery protocol for decoding json.

    This class fires a deferred with the decoded json in dictionary format.
    '''

    def __init__(self, deferred):
        self.deferred = deferred
        self.remaining = 1024*10
        self.dataBuffer = ''

    def dataReceived(self, bytes):
        self.dataBuffer += bytes

    def connectionLost(self, reason):
        data = json.loads(self.dataBuffer)
        if data.has_key('error'):
            self.deferred.errback(
                lastfmapi.LastFmApiException(data['message']))
        else:
            self.deferred.callback(data)


class LastFmApi(lastfmapi.LastFmApi):
    '''An twisted interface to lastfmapi.LastFmApi.'''

    def __init__(self, key):
        lastfmapi.LastFmApi.__init__(self, key)
        self.agent = Agent(reactor)

    def __send(self, params):

        def callback(response):
            deferred = Deferred()
            response.deliverBody(JSONDecoder(deferred))
            return deferred

        params['api_key'] = self.__api_key
        params['format'] = 'json'
        params = urllib.urlencode(params)

        headers = Headers({
            'User-Agent:': ['txlastfamapi'],
        })

        deferred = self.agent.request(
            'GET',
            '%s?%s' %(lastfmapi.LASTFM_API_ENDPOINT, params),
            headers,
            None)
        deferred.addCallback(callback)
        return deferred
