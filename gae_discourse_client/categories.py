"""Gateway for accessing the Discourse API (for forums)"""

import json
import re
from urllib import urlencode

from google.appengine.api import urlfetch
from google.appengine.ext import ndb


class Error(Exception):
    pass


class CategoryClient(object):
    """An API client for interacting with Discourse for category-related actions"""

    def __init__(self, api_client):
        self._api_client = api_client

    @ndb.tasklet
    def getByName(self, category_name, parent_category_name=None):
        if parent_category_name:
            parent_category = yield self.getByName(parent_category_name)
            if not parent_category:
                raise ndb.Return(None)

            categories = yield self._api_client.getRequest('categories.json', params={'parent_category_id': parent_category['id']})
        else:
            categories = yield self._api_client.getRequest('categories.json')

        for category in categories['category_list']['categories']:
            if category['name'] == category_name:
                raise ndb.Return(category)

        raise ndb.Return(None)

    @ndb.tasklet
    def create(self, category_name, parent_category_name=None, strict=False, **kwargs):
        """Create a category"""
        category = yield self.getByName(category_name, parent_category_name)
        if category:
            if not strict:
                raise ndb.Return(None)
            else:
                raise Error("Category named %s already exists!" % category_name)

        payload = {
            'name': category_name,
            'allow_badges': True,
            'color': 'FFFFFF',
            'text_color': '000000'
        }

        for k, v in kwargs.iteritems():
            payload[k] = v

        if parent_category_name:
            parent_category = yield self.getByName(parent_category_name)
            if not parent_category:
                raise Error("Could not find category named %s" % parent_category_name)
            payload['parent_category_id'] = parent_category['id']

        response = yield self._api_client.postRequest('categories', payload=payload)
        raise ndb.Return(response)

    @ndb.tasklet
    def delete(self, category_name, parent_category_name=None, strict=False):
        category = yield self.getByName(category_name, parent_category_name)
        if not category:
            if not strict:
                raise ndb.Return(None)
            else:
                raise Error("Could not find category named %s" % category_name)

        response = yield self._api_client.deleteRequest('categories/%s' % category['slug'])
        raise ndb.Return(response)
