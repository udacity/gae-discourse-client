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
        response = discourse_client.content.get(15).get_result() # Staff category
        self.assertEqual(4, len(response))

        for topic in response:
            response = discourse_client.content.getTopic(topic['id']).get_result()
            self.assertTrue(0 < len(response))
            for post in response:
                self.assertTrue('cooked' in post)
