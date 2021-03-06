import json

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import urlfetch_stub
from google.appengine.ext import ndb

from gae_discourse_client import discourse_client
import base


class DiscourseContentUnitTestCase(base.TestCase):
    def setUp(self):
        super(DiscourseContentUnitTestCase, self).setUp()
        self.credentials = {'api_key': 'super-secret-key', 'api_username': 'system'}

        apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
        apiproxy_stub_map.apiproxy.RegisterStub(
            'urlfetch', urlfetch_stub.URLFetchServiceStub())

        discourse_client.initClient(
            'http://rants.example.com/',
            self.credentials['api_key'],
            self.credentials['api_username']
        )

    def testGetPosts(self):
        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({'topic_list': {'topics': [
            {
                'id': 1,
                'title': 'Who is the greatest band of all time?',
                'slug': 'who-is-greatest-band',
                'excerpt': 'The Beatles, obviously'
            },
            {
                'id': 2,
                'title': 'How does Randy Moss access his memory?',
                'slug': 'randy-moss-memory',
                'excerpt': 'Straight Cache, Homey'
            }
        ]}})
        self._expectUrlfetch(url='http://rants.example.com/c/17.json', method='GET', payload='', response=response)

        discourse_client.content.getTopics(category_id=17).get_result()

    def testGetSubcategoryPosts(self):
        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({'topic_list': {'topics': [
            {
                'id': 1,
                'title': 'Who is the greatest band of all time?',
                'slug': 'who-is-greatest-band',
                'excerpt': 'The Beatles, obviously'
            },
            {
                'id': 2,
                'title': 'How does Randy Moss access his memory?',
                'slug': 'randy-moss-memory',
                'excerpt': 'Straight Cache, Homey'
            }
        ]}})
        self._expectUrlfetch(url='http://rants.example.com/c/23/17.json', method='GET', payload='', response=response)

        discourse_client.content.getTopics(category_id=17, parent_category_id=23).get_result()

    def testGetLastPost(self):
        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({
            'id': 1,
            'post_number': 1,
            'cooked': '<p>Buddy the Elf, whats your favorite color?</p>'
        })
        self._expectUrlfetch(url='http://rants.example.com/t/13/last.json', method='GET', payload='', response=response)

        discourse_client.content.getTopicLast(topic_id=13).get_result()
