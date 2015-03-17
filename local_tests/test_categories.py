import json

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import urlfetch_stub
from google.appengine.ext import ndb

from gae_discourse_client import discourse_client
from gae_discourse_client import categories
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

    def testCreateCategory(self):
        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({'category_list': {'categories': []}})
        self._expectUrlfetch(url='http://rants.example.com/categories.json', method='GET', payload='', response=response)

        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({'success': True})
        self._expectUrlfetch(url='http://rants.example.com/categories', method='POST', payload='', response=response)

        discourse_client.categories.create(
            category_name='Football Players'
        ).get_result()

    def testCreateSubcategory(self):
        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({'category_list': {'categories': [{'name': 'Football Players', 'id': 55}]}})
        self._expectUrlfetch(url='http://rants.example.com/categories.json', method='GET', payload='', response=response)

        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({'category_list': {'categories': []}})
        self._expectUrlfetch(url='http://rants.example.com/categories.json?parent_category_id=55', method='GET', payload='', response=response)

        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({'category_list': {'categories': [{'name': 'Football Players', 'id': 55}]}})
        self._expectUrlfetch(url='http://rants.example.com/categories.json', method='GET', payload='', response=response)

        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({'success': True})
        self._expectUrlfetch(url='http://rants.example.com/categories', method='POST', payload='', response=response)

        discourse_client.categories.create(
            category_name='Denver Broncos',
            parent_category_name='Football Players'
        ).get_result()

    def testCreateSubcategoryFailsWhenParentNotFound(self):
        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({'category_list': {'categories': []}})
        self._expectUrlfetch(url='http://rants.example.com/categories.json', method='GET', payload='', response=response)

        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({'category_list': {'categories': []}})
        self._expectUrlfetch(url='http://rants.example.com/categories.json', method='GET', payload='', response=response)

        with self.assertRaises(categories.Error):
            discourse_client.categories.create(
                category_name='Denver Broncos',
                parent_category_name='Football Players'
            ).get_result()

    def testDeleteCategory(self):
        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({'category_list': {'categories': [{'name': 'Football Players', 'id': 55, 'slug': 'football-players'}]}})
        self._expectUrlfetch(url='http://rants.example.com/categories.json', method='GET', payload='', response=response)

        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({'success': True})
        self._expectUrlfetch(url='http://rants.example.com/categories/football-players', method='DELETE', payload='', response=response)

        discourse_client.categories.delete(
            category_name='Football Players'
        ).get_result()

    def testCreateCategoryFails(self):
        response = self.mock()
        response.status_code = 200
        response.content = json.dumps({'category_list': {'categories': []}})
        self._expectUrlfetch(url='http://rants.example.com/categories.json', method='GET', payload='', response=response)

        response = self.mock()
        response.status_code = 403
        response.content = json.dumps({'success': False})
        self._expectUrlfetch(url='http://rants.example.com/categories', method='POST', payload='', response=response)

        with self.assertRaises(discourse_client.Error):
            discourse_client.categories.create(
                category_name='Football Players'
            ).get_result()
