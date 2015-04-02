import json
import os
import unittest

from multidimensional_urlencode import urlencode

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import urlfetch_stub
from google.appengine.ext import testbed

from gae_discourse_client import discourse_client


class DiscourseUserTestCase(unittest.TestCase):
    def setUp(self):
        super(DiscourseUserTestCase, self).setUp()

        apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
        apiproxy_stub_map.apiproxy.RegisterStub(
            'urlfetch', urlfetch_stub.URLFetchServiceStub())

        discourse_client.initClient(
            os.environ['DISCOURSE_URL'],
            os.environ['DISCOURSE_API_KEY'],
            'system'
        )

    def testDeleteUser(self):
        response = discourse_client.users.create(
            name='Peyton Manning',
            email='peyton@example.com',
            password='omaha, omaha',
            username='peyton18'
        ).get_result()

        user = discourse_client.users.getByEmail(
            user_email='peyton@example.com'
        ).get_result()

        response = discourse_client.users.delete('peyton@example.com').get_result()

        self.assertTrue(response['deleted'])

    def testCreateUser(self):
        discourse_client.users.delete('peyton@example.com').get_result()

        response = discourse_client.users.create(
            name='Peyton Manning',
            email='peyton@example.com',
            password='omaha, omaha',
            username='peyton18'
        ).get_result()

        self.assertTrue(response['success'])

    def testFindUserByEmail(self):
        response = discourse_client.users.create(
            name='Peyton Manning',
            email='peyton@example.com',
            password='omaha, omaha',
            username='peyton18'
        ).get_result()

        response = discourse_client.users.getByEmail(
            user_email='peyton@example.com'
        ).get_result()

        self.assertEqual('peyton18', response['username'])
