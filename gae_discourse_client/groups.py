"""Gateway for accessing the Discourse API (for forums)"""

import json
import re

from google.appengine.api import urlfetch
from google.appengine.ext import ndb


class Error(Exception):
    pass


class GroupClient(object):
    """An API client for interacting with Discourse for group-related actions"""

    def __init__(self, api_client, user_client):
        self._api_client = api_client
        self._user_client = user_client

    @ndb.tasklet
    def addUser(self, user_email, group_name):
        """Adds the given account to the Discourse group with the given name

        Args:
          user_email: Email address of the user to add.
          group_name: Name of the group to which we want to add the user.

        Returns:
          A dictionary object with the key 'success' set to True if the user was successfully
          added.

        Raises:
          Error: If the user or group was not found.
        """

        user = yield self._user_client.getByEmail(user_email)
        if not user:
            raise Error("Unable to find user with email %s" % user_email)

        group = yield self.getByName(group_name)
        if not group:
            raise Error("Group named %s not found" % group_name)

        payload = {
            'usernames': user['username']
        }

        result = yield self._api_client.putRequest(
            'admin/groups/%s/members.json' % group['id'], payload=payload
        )
        raise ndb.Return(result)

    @ndb.tasklet
    def removeUser(self, user_email, group_name):
        """Removes an account from a group

        Args:
          user_email: Email address of the user to remove.
          group_name: Name of the group from which we want to remove the user.

        Returns:
          A dictionary object with the key 'success' set to True if the user was successfully
          removed, False otherwise.

        Raises:
          Error: If the user or group was not found.
        """

        user = yield self._user_client.getByEmail(user_email)
        if not user:
            raise Error("Unable to find user with email %s" % user_email)

        group = yield self.getByName(group_name)
        if not group:
            raise Error("Group named %s not found" % group_name)

        result = yield self._api_client.deleteRequest(
            'admin/groups/%s/members.json' % group['id'],
            params={'user_id': user['id']}
        )
        raise ndb.Return(result)

    @ndb.tasklet
    def create(self, group_name, strict=False, **kwargs):
        """Creates a group with the given name on Discourse.

        Args:
          group_name: Name of the group to create.
          strict: Whether to enforce that a group is actually created. If this is False and the
            group already exists, this is a no-op.
          kwargs: Any additional keyword arguments to pass to the admin/groups endpoint.

        Returns:
          A dictionary object with key 'success' set to True if the group was successfully
            created. If the group already exists and `strict` is False, returns None.

        Raises:
          Error: if `strict` is True and the group already exists.
        """

        group = yield self.getByName(group_name)
        if group:
            if not strict:
                raise ndb.Return(None)
            else:
                raise Error("Group named %s already exists!" % group_name)

        payload = {
            'name': group_name
        }

        for k, v in kwargs.iteritems():
            payload[k] = v

        response = yield self._api_client.postRequest('admin/groups', payload=payload)
        raise ndb.Return(response)

    @ndb.tasklet
    def delete(self, group_name, strict=False):
        """Delete a group.

        Args:
          group_name: Name of the group to delete.
          strict: Whether to enforce that a group is actually deleted. If this is False and the
            group does not exist, this is a no-op.

        Returns:
          A dictionary object with key 'success' set to True if the group was successfully
            deleted. If the group does not exist and `strict` is False, returns None.

        Raises:
          Error: if `strict` is True and the group already exists.
        """
        group = yield self.getByName(group_name)
        if not group:
            if not strict:
                raise ndb.Return(None)
            else:
                raise Error("Could not find group with name %s" % group_name)

        response = yield self._api_client.deleteRequest('admin/groups/%s' % group['id'])
        raise ndb.Return(response)

    @ndb.tasklet
    def getByName(self, group_name):
        """Finds the Discourse group with the given name.

        Args:
          group_name: The name of the group to find.

        Returns:
          A dictionary containing information about the group if the group is successfully found,
          None otherwise
        """
        groups = yield self._api_client.getRequest('admin/groups.json')

        for group in groups:
            if group['name'] == group_name:
                raise ndb.Return(group)

        raise ndb.Return(None)
