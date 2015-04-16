"""Module for accessing and creating content through the Discourse API"""

from google.appengine.ext import ndb


class Error(Exception):
    pass


class ContentClient(object):
    """An API client for interacting with Discourse for content-related actions"""

    def __init__(self, api_client, category_client):
        self._api_client = api_client
        self._category_client = category_client

    @ndb.tasklet
    def get(self, category_slug=None, parent_category_slug=None):
        """Gets all posts for the given category.

        Args:
          category_slug: Slug for the category from which to retrieve posts, if any.
          parent_category_slug: Slug for the parent category, if any. If this is None, a toplevel
            category will be used.

        Returns:
          A list of Python objects representing Discourse posts.
        """

        category = yield self._category_client.getBySlug(category_slug, parent_category_slug)
        if not category:
            raise Error('Unable to find category with slug %s, parent slug %s'
                        % (category_slug, parent_category_slug))

        response = yield self._api_client.getRequest('c/%s.json' % category['id'])
        raise ndb.Return(response['topic_list']['topics'])
