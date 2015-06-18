import json
import os
import unittest

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import urlfetch_stub
from google.appengine.ext import testbed

from gae_discourse_client import discourse_client


class DiscourseContentTestCase(unittest.TestCase):
    def setUp(self):
        super(DiscourseContentTestCase, self).setUp()

        apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
        apiproxy_stub_map.apiproxy.RegisterStub(
            'urlfetch', urlfetch_stub.URLFetchServiceStub())

        discourse_client.initClient(
            os.environ['DISCOURSE_URL'],
            os.environ['DISCOURSE_API_KEY'],
            'system'
        )

    def testGetStaffPosts(self):
        response = discourse_client.content.getTopics(4).get_result() # Staff category
        self.assertEqual(6, len(response['topic_list']['topics']))

        for topic in response['topic_list']['topics']:
            response = discourse_client.content.getTopic(topic['id']).get_result()
            last = discourse_client.content.getTopicLast(topic['id']).get_result()

            self.assertTrue(0 < len(response['post_stream']['posts']))
            self.assertTrue(response['highest_post_number'] == last['post_stream']['posts'][-1]['post_number'])
            for post in response['post_stream']['posts']:
                self.assertTrue('cooked' in post)
