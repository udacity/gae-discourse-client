import json
from urllib import urlencode

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import urlfetch_stub
from google.appengine.ext import ndb

from gae_discourse_client import discourse_client
import base


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

    def testAddUserToGroupByEmail(self):
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

        discourse_client.groups.addUserByEmail('peyton18@example.com', 'quarterbacks').get_result()

    def testAddUserToGroupByUsername(self):
        response = self.mock()
        response.status_code = 200
        response.content = json.dumps([{'name': 'quarterbacks', 'id': 32}])
        self._expectUrlfetch(url='http://rants.example.com/admin/groups.json', method='GET', payload='', response=response)

        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({'success': True})
        payload = urlencode({'usernames': 'peyton18'})
        self._expectUrlfetch(url='http://rants.example.com/admin/groups/32/members.json', method='PUT', payload=payload, response=response)

        discourse_client.groups.addUserByUsername('peyton18', 'quarterbacks').get_result()

    def testAddUserFailsWhenUserNotFound(self):
        response = self.mock()
        response.status_code = 404
        response.content = json.dumps([])
        self._expectUrlfetch(url='http://rants.example.com/admin/users/list/active.json?filter=peyton18%40example.com&show_emails=true', method='GET', payload='', response=response)

        with self.assertRaises(discourse_client.Error):
            discourse_client.groups.addUserByEmail('peyton18@example.com', 'quarterbacks').get_result()

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
            discourse_client.groups.addUserByEmail('peyton18@example.com', 'quarterbacks').get_result()

    def testRemoveUserFromGroupByEmail(self):
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

        discourse_client.groups.removeUserByEmail('peyton18@example.com', 'quarterbacks').get_result()

    def testRemoveUserFromGroupByUsername(self):
        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({'email': 'peyton18@example.com', 'id': 18, 'username': 'peyton18'})
        self._expectUrlfetch(url='http://rants.example.com/admin/users/peyton18.json', method='GET', payload='', response=response)

        response = self.mock()
        response.status_code = 200
        response.content = json.dumps([{'name': 'quarterbacks', 'id': 32}])
        self._expectUrlfetch(url='http://rants.example.com/admin/groups.json', method='GET', payload='', response=response)

        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({'success': True})
        self._expectUrlfetch(url='http://rants.example.com/admin/groups/32/members.json?user_id=18', method='DELETE', payload='', response=response)

        discourse_client.groups.removeUserByUsername('peyton18', 'quarterbacks').get_result()

    def testGetMembersReturnsGroupMembers(self):
        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({
            'members': [{
                'id': 18,
                'username': 'peyton18',
                'name': 'Peyton Manning'
            }, {
                'id': 12,
                'username': 'treebeard',
                'name': 'Andrew Luck'
            }],
            'meta': {
                'total': 2,
                'limit': 50,
                'offset': 0
            }
        })
        self._expectUrlfetch(
            url='http://rants.example.com/groups/quarterbacks/members.json', method='GET',
            payload='', response=response)

        response = discourse_client.groups.getMembers('quarterbacks').get_result()
        self.assertEqual(2, len(response['members']))
        self.assertEqual(2, response['meta']['total'])
        self.assertTrue(any(member['name'] == 'Andrew Luck' for member in response['members']))
