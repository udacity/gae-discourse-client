import json
from urllib import urlencode

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import urlfetch_stub
from google.appengine.ext import ndb

from gae_discourse_client import discourse_client
from tests.unit_tests import base


class DiscourseUserUnitTestCase(base.TestCase):
    def setUp(self):
        super(DiscourseUserUnitTestCase, self).setUp()
        self.credentials = {'api_key': 'super-secret-key', 'api_username': 'system'}

        apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
        apiproxy_stub_map.apiproxy.RegisterStub(
            'urlfetch', urlfetch_stub.URLFetchServiceStub())

        discourse_client.initClient(
            'http://rants.example.com/',
            self.credentials['api_key'],
            self.credentials['api_username']
        )

    def testCreateGroup(self):
        response = self.mock()
        response.status_code = 200
        response.content = json.dumps([])
        self._expectUrlfetch(url='http://rants.example.com/admin/groups.json', method='GET', payload='', response=response)

        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({'success': True})
        self._expectUrlfetch(url='http://rants.example.com/admin/groups', method='POST', payload='', response=response)

        discourse_client.groups.create(
            group_name='quarterbacks'
        ).get_result()

    def testDeleteGroup(self):
        response = self.mock()
        response.status_code = 200
        response.content = json.dumps([{'name': 'quarterbacks', 'id': 32}])
        self._expectUrlfetch(url='http://rants.example.com/admin/groups.json', method='GET', payload='', response=response)

        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({'deleted': True})
        self._expectUrlfetch(url='http://rants.example.com/admin/groups/32', method='DELETE', payload='', response=response)

        discourse_client.groups.delete('quarterbacks').get_result()

    def testAddUserToGroup(self):
        response = self.mock()
        response.status_code = 200
        response.content = json.dumps([{'email': 'peyton18@example.com', 'id': 18, 'username': 'peyton18'}])
        self._expectUrlfetch(url='http://rants.example.com/admin/users/list/active.json?filter=peyton18%40example.com&show_emails=true', method='GET', payload='', response=response)

        response = self.mock()
        response.status_code = 200
        response.content = json.dumps([{'name': 'quarterbacks', 'id': 32}])
        self._expectUrlfetch(url='http://rants.example.com/admin/groups.json', method='GET', payload='', response=response)

        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({'success': True})
        payload = urlencode({'usernames': 'peyton18'})
        self._expectUrlfetch(url='http://rants.example.com/admin/groups/32/members.json', method='PUT', payload=payload, response=response)

        discourse_client.groups.addUser('peyton18@example.com', 'quarterbacks').get_result()

    def testAddUserFailsWhenUserNotFound(self):
        response = self.mock()
        response.status_code = 404
        response.content = json.dumps([])
        self._expectUrlfetch(url='http://rants.example.com/admin/users/list/active.json?filter=peyton18%40example.com&show_emails=true', method='GET', payload='', response=response)

        with self.assertRaises(discourse_client.Error):
            discourse_client.groups.addUser('peyton18@example.com', 'quarterbacks').get_result()

    def testAddUserFailsWhenGroupNotFound(self):
        response = self.mock()
        response.status_code = 200
        response.content = json.dumps([{'email': 'peyton18@example.com', 'id': 18, 'username': 'peyton18'}])
        self._expectUrlfetch(url='http://rants.example.com/admin/users/list/active.json?filter=peyton18%40example.com&show_emails=true', method='GET', payload='', response=response)

        response = self.mock()
        response.status_code = 404
        response.content = json.dumps([])
        self._expectUrlfetch(url='http://rants.example.com/admin/groups.json', method='GET', payload='', response=response)

        with self.assertRaises(discourse_client.Error):
            discourse_client.groups.addUser('peyton18@example.com', 'quarterbacks').get_result()

    def testRemoveUserFromGroup(self):
        response = self.mock()
        response.status_code = 200
        response.content = json.dumps([{'email': 'peyton18@example.com', 'id': 18, 'username': 'peyton18'}])
        self._expectUrlfetch(url='http://rants.example.com/admin/users/list/active.json?filter=peyton18%40example.com&show_emails=true', method='GET', payload='', response=response)

        response = self.mock()
        response.status_code = 200
        response.content = json.dumps([{'name': 'quarterbacks', 'id': 32}])
        self._expectUrlfetch(url='http://rants.example.com/admin/groups.json', method='GET', payload='', response=response)

        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({'success': True})
        self._expectUrlfetch(url='http://rants.example.com/admin/groups/32/members.json?user_id=18', method='DELETE', payload='', response=response)

        discourse_client.groups.removeUser('peyton18@example.com', 'quarterbacks').get_result()
