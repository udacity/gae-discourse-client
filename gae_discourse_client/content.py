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
    def get(self, category_id=None, page=0):
        """Gets all posts for the given category.

        Args:
          category_id: ID for the category from which to retrieve posts, if any.
          page: Page from which to retrieve results. Each page will return 30 posts.

        Returns:
          A list of Python objects representing Discourse topics.
        """

        if category_id:
            response = yield self._api_client.getRequest('c/%s.json' % category_id, params={'page': page})
        else:
            response = yield self._api_client.getRequest('latest.json', params={'page': page})
        
        raise ndb.Return(response['topic_list']['topics'])

    @ndb.tasklet
    def getTopic(self, topic_id):
        """Get the topic with the given ID

        Args:
          topic_id: ID for the topic to retrieve.

        Returns:
          A list of Python objects representing the posts in the topic.
        """

        response = yield self._api_client.getRequest('t/%s.json' % topic_id)
        raise ndb.Return(response['post_stream']['posts'])
