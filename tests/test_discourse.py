import json
import unittest

from multidimensional_urlencode import urlencode

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import urlfetch_stub
from google.appengine.ext import testbed

from src import discourse


class DiscourseTestCase(unittest.TestCase):
    def setUp(self):
        super(DiscourseTestCase, self).setUp()
        self.discourse_api_client = discourse.DiscourseAPIClient(
            'http://localhost:4000/',
            '26ec02d02e4c2ab78ba10ca648bcadb7035a008a25120e6a6363c08ebbfeee8b',
            'system')

        apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
        apiproxy_stub_map.apiproxy.RegisterStub('urlfetch',
            urlfetch_stub.URLFetchServiceStub())

    # USER TESTS

    def testDeleteUser(self):
        response = self.discourse_api_client.createUser(
            name='Peyton Manning',
            email='peyton@example.com',
            password='omaha, omaha',
            username='peyton18'
        ).get_result()

        user = self.discourse_api_client.getUserByEmail(
            user_email='peyton@example.com'
        ).get_result()

        response = self.discourse_api_client.deleteUser('peyton@example.com').get_result()

        self.assertTrue(response['deleted'])

    def testCreateUser(self):
        self.discourse_api_client.deleteUser('peyton@example.com').get_result()

        response = self.discourse_api_client.createUser(
            name='Peyton Manning',
            email='peyton@example.com',
            password='omaha, omaha',
            username='peyton18'
        ).get_result()

        self.assertTrue(response['success'])

    def testFindUserByEmail(self):
        response = self.discourse_api_client.createUser(
            name='Peyton Manning',
            email='peyton@example.com',
            password='omaha, omaha',
            username='peyton18'
        ).get_result()

        response = self.discourse_api_client.getUserByEmail(
            user_email='peyton@example.com'
        ).get_result()

        self.assertEqual('peyton18', response['username'])

    # CATEGORY TESTS

    def testDeleteCategory(self):
        self.discourse_api_client.createCategory(
            category_name='Broncos',
            slug='broncos'
        ).get_result()

        response = self.discourse_api_client.deleteCategory('Broncos').get_result()

        self.assertEqual('OK', response['success'])

    def testCreateCategory(self):
        self.discourse_api_client.deleteCategory('Broncos').get_result()

        response = self.discourse_api_client.createCategory(
            category_name='Broncos',
            slug='broncos'
        ).get_result()

        self.assertTrue(response['category'] is not None)

    def testGetCategoryByName(self):
        response = self.discourse_api_client.createCategory(
            category_name='Broncos',
            slug='broncos'
        ).get_result()

        response = self.discourse_api_client.getCategoryByName('Broncos').get_result()

        self.assertEqual('Broncos', response['name'])

    # GROUP TESTS

    def testDeleteGroup(self):
        self.discourse_api_client.createGroup(
            group_name='quarterbacks'
        ).get_result()

        response = self.discourse_api_client.deleteGroup('quarterbacks').get_result()
        self.assertEqual('OK', response['success'])

    def testCreateGroup(self):
        self.discourse_api_client.deleteGroup('quarterbacks').get_result()

        response = self.discourse_api_client.createGroup(
            group_name='quarterbacks'
        ).get_result()

        self.assertTrue(response['basic_group'] is not None)

    def testAddUserToGroup(self):
        self.discourse_api_client.createGroup(
            group_name='quarterbacks'
        ).get_result()

        self.discourse_api_client.createUser(
            name='Peyton Manning',
            email='peyton@example.com',
            password='omaha, omaha',
            username='peyton18'
        ).get_result()

        response = self.discourse_api_client.addUserToGroup(
            user_email='peyton@example.com',
            group_name='quarterbacks'
        ).get_result()

        self.assertEqual('OK', response['success'])

    def testRemoveUserFromGroup(self):
        self.discourse_api_client.createGroup(
            group_name='quarterbacks'
        ).get_result()

        self.discourse_api_client.createUser(
            name='Peyton Manning',
            email='peyton@example.com',
            password='omaha, omaha',
            username='peyton18'
        ).get_result()

        self.discourse_api_client.addUserToGroup(
            user_email='peyton@example.com',
            group_name='quarterbacks'
        ).get_result()

        response = self.discourse_api_client.removeUserFromGroup(
            user_email='peyton@example.com',
            group_name='quarterbacks'
        ).get_result()

        self.assertEqual('OK', response['success'])
