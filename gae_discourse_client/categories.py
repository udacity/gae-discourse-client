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
        """Finds a Discourse category by name.

        Args:
          category_name: The name of the category to find.
          parent_category_name: The name of the parent category (if any). If this is None, a
            top-level category will returned.

        Returns:
          A dictionary containing information about the category if the category is successfully found,
          None otherwise
        """
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
        """Creates a category on Discourse.

        Args:
          category_name: Name of the category to create.
          parent_category_name: Name of the parent category. If this is None, a top-level category
            is created.
          strict: Whether to enforce that a category is actually created. If this is False and the
            category already exists, this is a no-op.
          kwargs: Any additional keyword arguments to pass to the categories endpoint.

        Returns:
          A dictionary object with key 'success' set to True if the category was successfully
            created. If the category already exists and `strict` is False, returns None.

        Raises:
          Error: if `strict` is True and the category already exists, or if the parent category
            given does not exist.
        """
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
        """Delete a category.

        Args:
          category_name: Name of the category to delete.
          parent_category_name: Name of the parent category of the category to be deleted. If this
            is None, a top-level category will be deleted.
          strict: Whether to enforce that a category is actually deleted. If this is False and the
            category does not exist, this is a no-op.

        Returns:
          A dictionary object with key 'success' set to True if the category was successfully
            deleted. If the category does not exist and `strict` is False, returns None.

        Raises:
          Error: if `strict` is True and the category already exists.
        """
        category = yield self.getByName(category_name, parent_category_name)
        if not category:
            if not strict:
                raise ndb.Return(None)
            else:
                raise Error("Could not find category named %s" % category_name)

        response = yield self._api_client.deleteRequest('categories/%s' % category['slug'])
        raise ndb.Return(response)
