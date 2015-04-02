import json

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

    def testCreateUser(self):
        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({'success': True})
        self._expectUrlfetch(url='http://rants.example.com/users/', method='POST', payload='', response=response)

        discourse_client.users.create(
            name='Peyton Manning',
            email='peyton18@example.com',
            password='omahaomaha',
            username='peyton18'
        ).get_result()

    def testCreateUserFailsRaisesError(self):
        response = self.mock()
        response.status_code = 403
        response.content = json.dumps({'success': False})
        self._expectUrlfetch(url='http://rants.example.com/users/', method='POST', payload='', response=response)

        with self.assertRaises(discourse_client.Error):
            discourse_client.users.create(
                name='Peyton Manning',
                email='peyton18@example.com',
                password='omahaomaha',
                username='peyton18'
            ).get_result()

    def testDeleteUser(self):
        response = self.mock()
        response.status_code = 200
        response.content = json.dumps([{'email': 'peyton18@example.com', 'id': 18}])
        self._expectUrlfetch(url='http://rants.example.com/admin/users/list/active.json?filter=peyton18%40example.com&show_emails=true', method='GET', payload='', response=response)

        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({'deleted': True})
        self._expectUrlfetch(url='http://rants.example.com/admin/users/18.json', method='DELETE', payload='', response=response)

        discourse_client.users.delete('peyton18@example.com').get_result()
