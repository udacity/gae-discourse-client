import chai
from urllib import urlencode

from google.appengine.ext import ndb


class TestCase(chai.Chai):
    def _expectUrlfetch(self, url, method, payload, response):
        if '?' in url:
            url, params = url.split('?')
        else:
            params = ''

        if method in ('GET', 'DELETE') and params:
            params += '&' + urlencode(self.credentials)
        elif method in ('GET', 'DELETE'):
            params = urlencode(self.credentials)
        elif payload:
            payload += '&' + urlencode(self.credentials)
        else:
            payload = urlencode(self.credentials)

        payload_matchers = [self.contains(s) for s in payload.split('&')]
        url_matchers = [self.contains(s) for s in params.split('&')] + [self.contains(url)]

        result = ndb.Future()
        result.set_result(response)

        self.expect(ndb.get_context(), 'urlfetch').args(url=self.all_of(*url_matchers), headers={'Content-Type': 'application/x-www-form-urlencoded'}, method=method, payload=self.all_of(*payload_matchers)).any_order().returns(result)
