import json
import os
import unittest

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
            os.environ['DISCOURSE_URL'],
            os.environ['DISCOURSE_API_KEY'],
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

    def testAddUserToGroupByEmail(self):
        discourse_client.groups.create(
            group_name='quarterbacks'
        ).get_result()

        discourse_client.users.create(
            name='Peyton Manning',
            email='peyton@example.com',
            password='omaha, omaha',
            username='peyton18'
        ).get_result()

        response = discourse_client.groups.addUserByEmail(
            user_email='peyton@example.com',
            group_name='quarterbacks'
        ).get_result()

        self.assertEqual('OK', response['success'])

    def testRemoveUserFromGroupByEmail(self):
        discourse_client.groups.create(
            group_name='quarterbacks'
        ).get_result()

        discourse_client.users.create(
            name='Peyton Manning',
            email='peyton@example.com',
            password='omaha, omaha',
            username='peyton18'
        ).get_result()

        discourse_client.groups.addUserByUsername(
            username='peyton18',
            group_name='quarterbacks'
        ).get_result()

        response = discourse_client.groups.removeUserByEmail(
            user_email='peyton@example.com',
            group_name='quarterbacks'
        ).get_result()

        self.assertEqual('OK', response['success'])

    def testAddUserToGroupByUsername(self):
        discourse_client.groups.create(
            group_name='quarterbacks'
        ).get_result()

        discourse_client.users.create(
            name='John Elway',
            email='john@example.com',
            password='go card',
            username='jelway7'
        ).get_result()

        response = discourse_client.groups.addUserByUsername(
            username='jelway7',
            group_name='quarterbacks'
        ).get_result()

        self.assertEqual('OK', response['success'])

    def testRemoveUserFromGroupByUsername(self):
        discourse_client.groups.create(
            group_name='quarterbacks'
        ).get_result()

        discourse_client.users.create(
            name='Peyton Manning',
            email='peyton@example.com',
            password='omaha, omaha',
            username='peyton18'
        ).get_result()

        discourse_client.groups.addUserByUsername(
            username='peyton18',
            group_name='quarterbacks'
        ).get_result()

        response = discourse_client.groups.removeUserByUsername(
            username='peyton18',
            group_name='quarterbacks'
        ).get_result()

        self.assertEqual('OK', response['success'])

    def testListGroupMembers(self):
        # delete the group if it exists
        try:
            response = discourse_client.groups.delete('coaches').get_result()
        except:
            pass

        discourse_client.groups.create(
            group_name='coaches'
        ).get_result()

        discourse_client.users.create(
            name='Mike Shanahan',
            email='shanahan@broncos.com',
            password='elwayelway97',
            username='shanahan'
        ).get_result()

        discourse_client.users.create(
            name='Mike Tomlin',
            email='tomlin@steelers.com',
            password='steelcity7',
            username='miket'
        ).get_result()

        discourse_client.groups.addUserByUsername(
            username='shanahan',
            group_name='coaches'
        ).get_result()

        discourse_client.groups.addUserByUsername(
            username='miket',
            group_name='coaches'
        ).get_result()

        response = discourse_client.groups.getMembers(
            group_name='coaches'
        ).get_result()

        self.assertEqual(2, response['meta']['total'])
        self.assertEqual(
            {'shanahan', 'miket'},
            set(member['username'] for member in response['members'])
        )
