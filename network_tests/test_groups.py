import json
import unittest

from multidimensional_urlencode import urlencode

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import urlfetch_stub
from google.appengine.ext import testbed

from gae_discourse_client import discourse_client


class DiscourseGroupTestCase(unittest.TestCase):
    def setUp(self):
        super(DiscourseGroupTestCase, self).setUp()

        apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
        apiproxy_stub_map.apiproxy.RegisterStub(
            'urlfetch', urlfetch_stub.URLFetchServiceStub())

        discourse_client.initClient(
            'http://localhost:4000/',
            '26ec02d02e4c2ab78ba10ca648bcadb7035a008a25120e6a6363c08ebbfeee8b',
            'system'
        )

    def testDeleteGroup(self):
        discourse_client.groups.create(
            group_name='quarterbacks'
        ).get_result()

        response = discourse_client.groups.delete('quarterbacks').get_result()
        self.assertEqual('OK', response['success'])

    def testCreateGroup(self):
        discourse_client.groups.delete('quarterbacks').get_result()

        response = discourse_client.groups.create(
            group_name='quarterbacks'
        ).get_result()

        self.assertTrue(response['basic_group'] is not None)

    def testAddUserToGroup(self):
        discourse_client.groups.create(
            group_name='quarterbacks'
        ).get_result()

        discourse_client.users.create(
            name='Peyton Manning',
            email='peyton@example.com',
            password='omaha, omaha',
            username='peyton18'
        ).get_result()

        response = discourse_client.groups.addUser(
            user_email='peyton@example.com',
            group_name='quarterbacks'
        ).get_result()

        self.assertEqual('OK', response['success'])

    def testRemoveUserFromGroup(self):
        discourse_client.groups.create(
            group_name='quarterbacks'
        ).get_result()

        discourse_client.users.create(
            name='Peyton Manning',
            email='peyton@example.com',
            password='omaha, omaha',
            username='peyton18'
        ).get_result()

        discourse_client.groups.addUser(
            user_email='peyton@example.com',
            group_name='quarterbacks'
        ).get_result()

        response = discourse_client.groups.removeUser(
            user_email='peyton@example.com',
            group_name='quarterbacks'
        ).get_result()

        self.assertEqual('OK', response['success'])
