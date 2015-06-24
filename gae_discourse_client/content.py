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
    def getTopics(self, category_id=None, parent_category_id=None, page=0):
        """Gets all topics for the given category.

        Args:
          category_id: ID for the category from which to retrieve posts, if any.
          page: Page from which to retrieve results. Each page will return 30 posts.

        Returns:
          Python object representation of the topics in the category. This includes a list of
          users and a list of topics.
        """

        if category_id and parent_category_id:
            response = yield self._api_client.getRequest(
                'c/%s/%s.json' % (parent_category_id, category_id), params={'page': page})
        elif category_id:
            response = yield self._api_client.getRequest(
                'c/%s.json' % category_id, params={'page': page})
        else:
            response = yield self._api_client.getRequest('latest.json', params={'page': page})

        raise ndb.Return(response)

    @ndb.tasklet
    def getTopic(self, topic_id):
        """Get the topic with the given ID

        Args:
          topic_id: ID for the topic to retrieve.

        Returns:
          Python object representation of the topic.
        """

        response = yield self._api_client.getRequest('t/%s.json' % topic_id)
        raise ndb.Return(response)

    @ndb.tasklet
    def getTopicLast(self, topic_id):
        """Get the last post in the topic with the given ID

        Args:
          topic_id: ID for the topic to retrieve.

        Returns:
          Python object representation of the post.
        """

        response = yield self._api_client.getRequest('t/%s/last.json' % topic_id)
        raise ndb.Return(response)
